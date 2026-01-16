"""
AutoML Backend - FastAPI Server
Main application file with API endpoints and app initialization.
All data processing and utility functions are imported from dedicated modules.
"""

# ==========================================
# IMPORTS
# ==========================================

# Standard Library
import os
import io
import uuid
import zipfile
import warnings
from contextlib import asynccontextmanager

# Data Processing
import pandas as pd
import numpy as np

# Visualization
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# FastAPI & Web
from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
import httpx

# Scheduling
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Custom modules
from notebook_utils import save_to_ipynb
from data_utils import load_csv_to_dataframe, get_df_info
from missing_values import handle_missing_values
from outliers import detect_and_handle_outliers
from analysis import univariate_analysis, bivariate_analysis
from correlation_utils import handle_high_correlation
from encoding_utils import handle_categorical_encoding
from scaling_utils import handle_feature_scaling
from column_ops import drop_columns_by_id
from storage import _load_df, _save_df, _log, _SESSION_LOGS
from schemas import (
    DropColumnsModel, MissingValuesPlan, OutlierPlan, 
    CorrelationPlan, EncodingPlan, ScalingPlan
)

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# ==========================================
# CONSTANTS & GLOBAL CONFIGURATION
# ==========================================

HEALTH_ENDPOINT_URL = "https://automl-1smu.onrender.com/health"
STORAGE_DIR = "temp_storage"
PLOTS_DIR = "plots"

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)


# ==========================================
# SCHEDULER & LIFECYCLE
# ==========================================

async def check_health_job():
    """Periodic health check job."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(HEALTH_ENDPOINT_URL)
            print(f"[Scheduler] Health check: {response.status_code}")
        except Exception as e:
            print(f"[Scheduler] Error: {e}")


scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan event handler for startup and shutdown."""
    # STARTUP
    scheduler.add_job(check_health_job, 'interval', minutes=10)
    scheduler.start()
    print("Scheduler started.")
    
    yield
    
    # SHUTDOWN
    scheduler.shutdown()
    print("Scheduler shutdown.")


# ==========================================
# FASTAPI APP INITIALIZATION
# ==========================================

app = FastAPI(
    title="AutoML EDA API",
    description="Automated exploratory data analysis and preprocessing",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
        "http://127.0.0.1",
        "https://auto-ml-mu.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# HEALTH CHECK ENDPOINTS
# ==========================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AutoML EDA API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "uptime": "ok"}


# ==========================================
# FILE UPLOAD & SESSION ENDPOINTS
# ==========================================

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Upload CSV file and create a new session."""
    session_id = str(uuid.uuid4())
    
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        _log(session_id, "Load Data", [
            f"file_path = '{file.filename}'",
            "df = pd.read_csv(file_path)",
            "print(df.shape)",
            "df.head()"
        ])
        
        # Save to memory
        _save_df(session_id, df)
        info = get_df_info(df)
        
        return {
            "session_id": session_id,
            "shape": df.shape,
            "columns": info.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error uploading file: {str(e)}")


@app.get("/info/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a session."""
    df = _load_df(session_id)
    return {
        "shape": df.shape,
        "columns": get_df_info(df).to_dict(orient="records")
    }


# ==========================================
# COLUMN MANAGEMENT ENDPOINTS
# ==========================================

@app.post("/clean/drop")
async def api_drop_columns(payload: DropColumnsModel):
    """Drop columns from the dataset."""
    df = _load_df(payload.session_id)
    cols = list(df.columns)
    to_drop = [cols[cid-1] for cid in payload.column_ids if 1 <= cid <= len(cols)]
    
    if to_drop:
        df = df.drop(columns=to_drop)
        _save_df(payload.session_id, df)
        _log(payload.session_id, "Drop Columns", [
            f"columns_to_drop = {to_drop}",
            "df.drop(columns=columns_to_drop, inplace=True)",
        ])
    
    return {"message": "ok", "columns": get_df_info(df).to_dict(orient="records")}


# ==========================================
# MISSING VALUES ENDPOINTS
# ==========================================

@app.get("/suggestions/missing/{session_id}")
async def api_missing_suggestions(session_id: str):
    """Get missing value handling suggestions."""
    df = _load_df(session_id)
    info_df = get_df_info(df)
    missing_cols = info_df[info_df['percentage_missing'] > 0]
    suggestions = {}
    
    for _, row in missing_cols.iterrows():
        col = row['column_name']
        pct = row['percentage_missing']
        dtype = df[col].dtype
        
        if pct > 50:
            action = 'drop_col'
        elif str(dtype) in ['object', 'category']:
            action = 'mode'
        else:
            skew = df[col].dropna().skew() if df[col].dropna().size else 0
            action = 'median' if abs(skew) > 1 else 'mean'
        
        suggestions[row['id']] = {
            "column": col,
            "missing_pct": pct,
            "suggested_action": action
        }
    
    return suggestions


@app.post("/clean/missing")
async def api_missing_apply(payload: MissingValuesPlan):
    """Apply missing value handling plan."""
    df = _load_df(payload.session_id)
    cols = list(df.columns)
    logs = []
    
    for action, ids in payload.plan.items():
        for cid in ids:
            if not (1 <= cid <= len(cols)):
                continue
            
            col = cols[cid-1]
            is_cat = str(df[col].dtype) in ['object', 'category']
            
            if action in ['mean', 'median'] and is_cat:
                try:
                    df[col] = pd.to_numeric(df[col], errors='raise')
                    logs.append(f"df['{col}'] = pd.to_numeric(df['{col}'], errors='raise')")
                except Exception:
                    continue
            
            if action == 'mean':
                val = df[col].mean()
                df[col] = df[col].fillna(val)
                logs.append(f"df['{col}'].fillna(df['{col}'].mean(), inplace=True)")
            
            elif action == 'median':
                val = df[col].median()
                df[col] = df[col].fillna(val)
                logs.append(f"df['{col}'].fillna(df['{col}'].median(), inplace=True)")
            
            elif action == 'mode':
                mode_val = df[col].mode()
                if not mode_val.empty:
                    df[col] = df[col].fillna(mode_val.iloc[0])
                    logs.append(f"df['{col}'].fillna(df['{col}'].mode()[0], inplace=True)")
            
            elif action == 'drop_col':
                df = df.drop(columns=[col])
                logs.append(f"df.drop(columns=['{col}'], inplace=True)")
    
    _save_df(payload.session_id, df)
    if logs:
        _log(payload.session_id, "Handle Missing Values", logs)
    
    return {"message": "ok", "columns": get_df_info(df).to_dict(orient="records")}


# ==========================================
# OUTLIER DETECTION & HANDLING ENDPOINTS
# ==========================================

@app.get("/suggestions/outliers/{session_id}")
async def api_outliers_suggestions(session_id: str):
    """Get outlier detection suggestions."""
    df = _load_df(session_id)
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    suggestions = {}
    
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        cnt = ((df[col] < (Q1 - 1.5*IQR)) | (df[col] > (Q3 + 1.5*IQR))).sum()
        pct = (cnt / len(df)) * 100
        
        if cnt > 0:
            col_id = df.columns.get_loc(col) + 1
            action = 'remove_rows' if pct > 10 else 'cap'
            suggestions[col_id] = {
                "column": col,
                "outliers_pct": round(pct, 2),
                "suggested_action": action
            }
    
    return suggestions


@app.post("/clean/outliers")
async def api_outliers_apply(payload: OutlierPlan):
    """Apply outlier handling plan."""
    df = _load_df(payload.session_id)
    cols = list(df.columns)
    logs = []
    
    for action, ids in payload.plan.items():
        for cid in ids:
            if not (1 <= cid <= len(cols)):
                continue
            
            col = cols[cid-1]
            if not pd.api.types.is_numeric_dtype(df[col]):
                continue
            
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
            
            if action == 'cap':
                df[col] = df[col].clip(lower=lower, upper=upper)
                logs.append(f"Q1=df['{col}'].quantile(0.25);Q3=df['{col}'].quantile(0.75);IQR=Q3-Q1;df['{col}']=df['{col}'].clip(Q1-1.5*IQR,Q3+1.5*IQR)")
            
            elif action == 'remove_rows':
                df = df[(df[col] >= lower) & (df[col] <= upper)]
                logs.append(f"Q1=df['{col}'].quantile(0.25);Q3=df['{col}'].quantile(0.75);IQR=Q3-Q1;df=df[(df['{col}']>=Q1-1.5*IQR)&(df['{col}']<=Q3+1.5*IQR)]")
    
    _save_df(payload.session_id, df)
    if logs:
        _log(payload.session_id, "Handle Outliers", logs)
    
    return {"message": "ok", "shape": df.shape}


# ==========================================
# CORRELATION & MULTICOLLINEARITY ENDPOINTS
# ==========================================

@app.post("/clean/correlation")
async def api_corr(payload: CorrelationPlan):
    """Handle high correlation between features."""
    df = _load_df(payload.session_id)
    nums = df.select_dtypes(include=['float64', 'int64']).columns
    
    if len(nums) < 2:
        return {"message": "not enough numeric columns"}
    
    corr_matrix = df[nums].corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    high_corr_cols = [c for c in upper.columns if any(upper[c] > payload.threshold)]
    logs = []
    
    if payload.auto_drop and high_corr_cols:
        df = df.drop(columns=high_corr_cols)
        logs.append(f"df.drop(columns={high_corr_cols}, inplace=True)")
        _save_df(payload.session_id, df)
        _log(payload.session_id, "Handle Multicollinearity", logs)
        return {"message": "auto-dropped", "dropped": high_corr_cols}
    
    if payload.plan and 'drop' in payload.plan:
        cols = list(df.columns)
        to_drop = [cols[cid-1] for cid in payload.plan['drop'] if 1 <= cid <= len(cols)]
        if to_drop:
            df = df.drop(columns=to_drop)
            logs.append(f"df.drop(columns={to_drop}, inplace=True)")
            _save_df(payload.session_id, df)
            _log(payload.session_id, "Handle Multicollinearity", logs)
            return {"message": "dropped", "dropped": to_drop}
    
    return {"message": "detected", "columns_to_drop": high_corr_cols}


# ==========================================
# CATEGORICAL ENCODING ENDPOINTS
# ==========================================

@app.get("/suggestions/encoding/{session_id}")
async def api_encoding_suggestions(session_id: str):
    """Get encoding suggestions for categorical columns."""
    df = _load_df(session_id)
    cats = df.select_dtypes(include=['object', 'category']).columns
    suggestions = {}
    
    for col in cats:
        col_id = df.columns.get_loc(col) + 1
        unique = df[col].nunique()
        action = 'one_hot' if unique <= 10 else 'label'
        suggestions[col_id] = {
            "column": col,
            "unique": int(unique),
            "suggested_action": action
        }
    
    return suggestions


@app.post("/clean/encoding")
async def api_encoding_apply(payload: EncodingPlan):
    """Apply categorical encoding."""
    df = _load_df(payload.session_id)
    cols = list(df.columns)
    logs = []
    
    if 'label' in payload.plan:
        from sklearn.preprocessing import LabelEncoder
        for cid in payload.plan['label']:
            if not (1 <= cid <= len(cols)):
                continue
            col = cols[cid-1]
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            logs.append(f"le=LabelEncoder(); df['{col}']=le.fit_transform(df['{col}'].astype(str))")
    
    if 'one_hot' in payload.plan:
        oh_cols = [cols[cid-1] for cid in payload.plan['one_hot'] if 1 <= cid <= len(cols)]
        if oh_cols:
            df = pd.get_dummies(df, columns=oh_cols, drop_first=True)
            logs.append(f"df=pd.get_dummies(df, columns={oh_cols}, drop_first=True)")
    
    _save_df(payload.session_id, df)
    if logs:
        _log(payload.session_id, "Categorical Encoding", logs)
    
    return {"message": "ok", "columns": get_df_info(df).to_dict(orient="records")}


# ==========================================
# FEATURE SCALING ENDPOINTS
# ==========================================

@app.get("/suggestions/scaling/{session_id}")
async def api_scaling_suggestions(session_id: str):
    """Get feature scaling suggestions."""
    df = _load_df(session_id)
    nums = df.select_dtypes(include=['float64', 'int64', 'int32']).columns
    suggestions = {}
    
    for col in nums:
        if df[col].nunique() <= 2:
            continue
        skew = float(df[col].skew())
        action = 'standard' if abs(skew) < 1 else 'minmax'
        suggestions[df.columns.get_loc(col) + 1] = {
            "column": col,
            "skew": round(skew, 2),
            "suggested_action": action
        }
    
    return suggestions


@app.post("/clean/scaling")
async def api_scaling_apply(payload: ScalingPlan):
    """Apply feature scaling."""
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    
    df = _load_df(payload.session_id)
    cols = list(df.columns)
    logs = []
    
    if 'standard' in payload.plan:
        std_cols = [cols[cid-1] for cid in payload.plan['standard'] if 1 <= cid <= len(cols)]
        if std_cols:
            scaler = StandardScaler()
            df[std_cols] = scaler.fit_transform(df[std_cols])
            logs.append(f"scaler=StandardScaler(); df[{std_cols}]=scaler.fit_transform(df[{std_cols}])")
    
    if 'minmax' in payload.plan:
        mm_cols = [cols[cid-1] for cid in payload.plan['minmax'] if 1 <= cid <= len(cols)]
        if mm_cols:
            scaler = MinMaxScaler()
            df[mm_cols] = scaler.fit_transform(df[mm_cols])
            logs.append(f"scaler=MinMaxScaler(); df[{mm_cols}]=scaler.fit_transform(df[{mm_cols}])")
    
    _save_df(payload.session_id, df)
    if logs:
        _log(payload.session_id, "Feature Scaling", logs)
    
    return {"message": "ok"}


# ==========================================
# ANALYSIS ENDPOINTS
# ==========================================

@app.get("/analysis/univariate/{session_id}")
async def api_univariate(session_id: str):
    """Get univariate analysis statistics."""
    df = _load_df(session_id)
    nums = df.select_dtypes(include=['float64', 'int64']).columns
    stats_df = df[nums].describe().T
    stats_df['skew'] = df[nums].skew().round(2)
    stats_df['%_zeros'] = (df[nums] == 0).mean().round(4) * 100
    
    _log(session_id, "Univariate Analysis", [
        "numeric_cols = df.select_dtypes(include=np.number).columns",
        "for col in numeric_cols:",
        "    fig, ax = plt.subplots(1, 2, figsize=(14, 5))",
        "    sns.histplot(df[col], kde=True, ax=ax[0])",
        "    sns.boxplot(x=df[col], ax=ax[1])",
        "    plt.show()"
    ])
    
    return stats_df.to_dict(orient="index")


@app.get("/analysis/bivariate/{session_id}")
async def api_bivariate(session_id: str):
    """Get bivariate analysis (correlation matrix)."""
    df = _load_df(session_id)
    nums = df.select_dtypes(include=['float64', 'int64']).columns
    corr = df[nums].corr()
    
    _log(session_id, "Bivariate Analysis", [
        "numeric_cols = df.select_dtypes(include=np.number).columns",
        "sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm')",
        "plt.show()",
        "sns.pairplot(df[numeric_cols])",
        "plt.show()"
    ])
    
    return corr.to_dict()


# ==========================================
# PLOT GENERATION ENDPOINTS
# ==========================================

@app.get("/plots/univariate/{session_id}/{column_name}")
async def api_plot_univariate(session_id: str, column_name: str, plot_types: str = "1"):
    """Generate univariate plots for a column.
    
    plot_types: comma-separated list of plot type IDs (1-5)
      1 = Histogram + Boxplot
      2 = Histogram with KDE
      3 = Boxplot + Swarmplot
      4 = Violin Plot
      5 = QQ Plot
    """
    df = _load_df(session_id)
    
    if column_name not in df.columns:
        raise HTTPException(status_code=404, detail=f"Column '{column_name}' not found")
    
    if not pd.api.types.is_numeric_dtype(df[column_name]):
        raise HTTPException(status_code=400, detail=f"Column '{column_name}' is not numeric")

    # Parse plot type IDs from query parameter
    selected_plots = set()
    try:
        for pt in plot_types.split(","):
            pt_id = int(pt.strip())
            if 1 <= pt_id <= 5:
                selected_plots.add(pt_id)
    except ValueError:
        selected_plots = {1}  # Default to histogram+boxplot

    if not selected_plots:
        selected_plots = {1}

    # Calculate statistics
    col = column_name
    mean_val = df[col].mean()
    median_val = df[col].median()
    skew_val = df[col].skew()
    zero_count = (df[col] == 0).sum()
    zero_pct = (zero_count / len(df[col]) * 100) if len(df[col]) > 0 else 0

    # Determine grid size
    num_plots = len(selected_plots)
    cols_per_row = 2
    rows = (num_plots + cols_per_row - 1) // cols_per_row

    fig, axes = plt.subplots(rows, cols_per_row, figsize=(14, 5 * rows))
    
    if rows == 1 and cols_per_row == 1:
        axes = [axes]
    elif rows == 1:
        axes = list(axes)
    else:
        axes = axes.flatten().tolist()

    ax_idx = 0

    if 1 in selected_plots:
        ax = axes[ax_idx]
        df[col].hist(bins=50, ax=ax, color="skyblue", edgecolor="black", alpha=0.8)
        ax.set_title("Histogram")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequency")
        ax.grid(alpha=0.3)
        ax_idx += 1

        ax = axes[ax_idx]
        df.boxplot(column=col, ax=ax, patch_artist=True, boxprops=dict(facecolor="lightcoral"), medianprops=dict(color="black"))
        ax.set_title("Boxplot")
        ax.grid(alpha=0.3)
        ax_idx += 1

    if 2 in selected_plots:
        ax = axes[ax_idx]
        df[col].hist(bins=50, ax=ax, color="lightblue", alpha=0.7, density=True)
        df[col].plot.density(ax=ax, color="red", linewidth=2, label="KDE")
        ax.axvline(mean_val, color="green", linestyle="--", label=f"Mean: {mean_val:.2f}")
        ax.axvline(median_val, color="orange", linestyle="--", label=f"Median: {median_val:.2f}")
        ax.set_title(f"Histogram + KDE\nSkew: {skew_val:.2f} | Zeros: {zero_pct:.1f}%")
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)
        ax_idx += 1

    if 3 in selected_plots:
        ax = axes[ax_idx]
        sns.boxplot(y=df[col], ax=ax, color="lightblue")
        sns.swarmplot(y=df[col], ax=ax, color="black", alpha=0.5, size=3)
        ax.set_title("Boxplot + Swarmplot")
        ax_idx += 1

    if 4 in selected_plots:
        ax = axes[ax_idx]
        sns.violinplot(y=df[col], ax=ax, inner="quartile", color="lightgreen")
        ax.set_title("Violin Plot")
        ax_idx += 1

    if 5 in selected_plots:
        ax = axes[ax_idx]
        stats.probplot(df[col], dist="norm", plot=ax)
        ax.set_title("QQ Plot (vs Normal)")
        ax.grid(alpha=0.3)
        ax_idx += 1

    # Hide unused subplot axes
    for j in range(ax_idx, len(axes)):
        axes[j].set_visible(False)

    plt.suptitle(f"Univariate Analysis: {col}", fontsize=16, fontweight="bold")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return Response(content=buf.getvalue(), media_type="image/png")


@app.get("/plots/univariate/{session_id}")
async def api_plot_all_univariate(session_id: str):
    """Generate all univariate plots as a ZIP archive."""
    df = _load_df(session_id)
    nums = df.select_dtypes(include=['float64', 'int64']).columns
    
    if len(nums) == 0:
        raise HTTPException(status_code=400, detail="No numeric columns found")
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for col in nums:
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))
            
            sns.histplot(df[col], kde=True, ax=axes[0], color='skyblue')
            axes[0].set_title(f'Distribution of {col}')
            axes[0].grid(alpha=0.3)
            
            sns.boxplot(x=df[col], ax=axes[1], color='lightcoral')
            axes[1].set_title(f'Boxplot of {col}')
            axes[1].grid(alpha=0.3)
            
            plt.tight_layout()
            
            img_buf = io.BytesIO()
            plt.savefig(img_buf, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            img_buf.seek(0)
            
            filename = f"{col.replace(' ', '_')}_univariate.png"
            zipf.writestr(filename, img_buf.getvalue())
    
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=univariate_plots.zip"},
    )


@app.get("/plots/bivariate/heatmap/{session_id}")
async def api_plot_heatmap(session_id: str, method: str = "pearson"):
    """Generate correlation heatmap."""
    df = _load_df(session_id)
    nums = df.select_dtypes(include=['float64', 'int64']).columns
    
    if len(nums) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 numeric columns")
    
    fig, ax = plt.subplots(figsize=(12, 10))
    corr = df[nums].corr(method=method)
    
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', vmin=-1, vmax=1,
                linewidths=0.5, linecolor='white', ax=ax, square=True)
    ax.set_title(f'Correlation Heatmap ({method.capitalize()})', fontsize=16, pad=20)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return Response(content=buf.getvalue(), media_type="image/png")


@app.get("/plots/bivariate/pairplot/{session_id}")
async def api_plot_pairplot(session_id: str, max_cols: int = 10):
    """Generate pairplot."""
    df = _load_df(session_id)
    nums = df.select_dtypes(include=['float64', 'int64']).columns
    
    if len(nums) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 numeric columns")
    
    if len(nums) > max_cols:
        nums = nums[:max_cols]
    
    pairplot_fig = sns.pairplot(df[nums], diag_kind='kde', plot_kws={'alpha': 0.6})
    pairplot_fig.fig.suptitle('Pairplot of Numeric Features', y=1.02, fontsize=16)
    
    buf = io.BytesIO()
    pairplot_fig.fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(pairplot_fig.fig)
    
    return Response(content=buf.getvalue(), media_type="image/png")


# ==========================================
# DOWNLOAD ENDPOINTS
# ==========================================

@app.post("/download/notebook")
async def api_download_notebook(
    session_id: str = Body(..., embed=True),
    filename: str = Body("workflow", embed=True)
):
    """Download preprocessing workflow as Jupyter notebook."""
    logs = _SESSION_LOGS.get(session_id, [])
    if not logs:
        raise HTTPException(status_code=404, detail="No logs found for session")
    
    save_to_ipynb(logs, filename=f"{filename}.ipynb")
    return FileResponse(
        os.path.abspath(filename + ".ipynb"),
        filename=filename + ".ipynb"
    )


@app.get("/download/csv/{session_id}")
async def api_download_csv(session_id: str):
    """Download cleaned dataset as CSV."""
    df = _load_df(session_id)  # This will raise 404 if not found
    
    # Create temp file for download
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
        df.to_csv(tmp.name, index=False)
        tmp_path = tmp.name
    
    return FileResponse(
        os.path.abspath(tmp_path),
        filename="clean_data.csv",
        media_type="text/csv"
    )


# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
