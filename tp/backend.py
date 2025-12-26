import pandas as pd
import numpy as np
from pandas.api.types import is_object_dtype, is_categorical_dtype
import matplotlib
matplotlib.use('Agg') # Prevent GUI errors on server
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
import json
import os
import shutil
import uuid
import warnings
from typing import List, Dict, Optional, Any, Union
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Body
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient

warnings.filterwarnings("ignore", category=FutureWarning)

# ==========================================
# 1. DATABASE & APP CONFIGURATION
# ==========================================
app = FastAPI(title="AutoEDA API with MongoDB")

# MongoDB Setup
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["auto_eda_db"]
sessions_col = db["sessions"]

# Storage Setup
STORAGE_DIR = "temp_storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

# ==========================================
# 2. DATA MODELS (Pydantic)
# ==========================================
class DropColumnsModel(BaseModel):
    session_id: str
    column_ids: List[int]

class MissingValuesPlan(BaseModel):
    session_id: str
    # Format: {"mean": [1, 2], "drop_col": [3], "mode": [4]}
    plan: Dict[str, List[int]] 

class OutlierPlan(BaseModel):
    session_id: str
    # Format: {"cap": [1, 2], "remove_rows": [3], "none": [4]}
    plan: Dict[str, List[int]]

class CorrelationPlan(BaseModel):
    session_id: str
    threshold: float = 0.90
    # Format: {"drop": [1, 2], "keep": [3]}
    plan: Optional[Dict[str, List[int]]] = None
    auto_drop: bool = False # If true, automatically drops suggested

class EncodingPlan(BaseModel):
    session_id: str
    # Format: {"one_hot": [1], "label": [2]}
    plan: Dict[str, List[int]]

class ScalingPlan(BaseModel):
    session_id: str
    # Format: {"standard": [1], "minmax": [2]}
    plan: Dict[str, List[int]]

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def get_session_file_path(session_id: str):
    return os.path.join(STORAGE_DIR, f"{session_id}.parquet")

def load_df(session_id: str):
    path = get_session_file_path(session_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Session file not found.")
    return pd.read_parquet(path)

def save_df(session_id: str, df: pd.DataFrame):
    path = get_session_file_path(session_id)
    df.to_parquet(path, index=False)

def update_mongo_logs(session_id: str, step_name: str, code_lines: List[str]):
    sessions_col.update_one(
        {"session_id": session_id},
        {"$push": {"logs": {"step": step_name, "code": code_lines}}}
    )

def get_df_info_dict(df):
    """Returns column info as a JSON-serializable list of dicts."""
    unique_percentages = (df.nunique() / len(df)) * 100
    missing_percentages = (df.isnull().sum() / len(df)) * 100
    
    info_list = []
    for idx, col in enumerate(df.columns):
        info_list.append({
            "id": idx + 1,
            "column_name": col,
            "dtype": str(df[col].dtype),
            "percentage_unique": round(unique_percentages[col], 2),
            "percentage_missing": round(missing_percentages[col], 2)
        })
    return info_list

# ==========================================
# 4. API ENDPOINTS
# ==========================================

@app.get("/")
def health_check():
    return {"status": "running", "database": "mongodb"}

# --- 1. LOAD DATA ---
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    file_location = get_session_file_path(session_id)
    
    # Save Uploaded File temporarily to read, then convert to Parquet for speed
    temp_csv = f"{file_location}.csv"
    with open(temp_csv, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        df = pd.read_csv(temp_csv)
        # Save as parquet for efficient session handling
        df.to_parquet(file_location, index=False)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")
    finally:
        if os.path.exists(temp_csv):
            os.remove(temp_csv)

    # Initialize MongoDB Entry
    log_entry = {
        "step": "Load Data", 
        "code": [
            f"file_path = '{file.filename}'", 
            "df = pd.read_csv(file_path)", 
            "print(df.shape)", 
            "df.head()"
        ]
    }
    
    sessions_col.insert_one({
        "session_id": session_id,
        "filename": file.filename,
        "logs": [log_entry],
        "created_at": pd.Timestamp.now().isoformat()
    })
    
    return {
        "session_id": session_id,
        "message": "File uploaded successfully",
        "shape": df.shape,
        "columns": get_df_info_dict(df)
    }

@app.get("/info/{session_id}")
def get_dataset_info(session_id: str):
    df = load_df(session_id)
    return {
        "shape": df.shape,
        "columns": get_df_info_dict(df)
    }

# --- 2. DROP COLUMNS ---
@app.post("/clean/drop")
def drop_columns(payload: DropColumnsModel):
    df = load_df(payload.session_id)
    
    # Map IDs to names
    cols_to_drop = []
    current_cols = list(df.columns)
    for cid in payload.column_ids:
        if 1 <= cid <= len(current_cols):
            cols_to_drop.append(current_cols[cid-1])
            
    if cols_to_drop:
        df.drop(columns=cols_to_drop, inplace=True)
        save_df(payload.session_id, df)
        
        # Log
        code = [
            f"cols_to_drop = {cols_to_drop}",
            "df.drop(columns=cols_to_drop, inplace=True)",
            "print(f'Dropped: {cols_to_drop}')"
        ]
        update_mongo_logs(payload.session_id, "Drop Columns", code)
        
    return {"message": "Columns dropped", "remaining_columns": get_df_info_dict(df)}

# --- 3. MISSING VALUES ---
@app.get("/suggestions/missing/{session_id}")
def suggest_missing(session_id: str):
    df = load_df(session_id)
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    
    suggestions = {}
    for col in missing.index:
        pct = (missing[col] / len(df)) * 100
        col_id = df.columns.get_loc(col) + 1
        dtype = df[col].dtype
        
        if pct > 50: action = 'drop_col'
        elif is_object_dtype(df[col]): action = 'mode'
        elif abs(df[col].dropna().skew()) > 1: action = 'median'
        else: action = 'mean'
        
        suggestions[col_id] = {
            "column": col, 
            "missing_pct": round(pct, 2), 
            "suggested_action": action
        }
        
    return suggestions

@app.post("/clean/missing")
def apply_missing_plan(payload: MissingValuesPlan):
    df = load_df(payload.session_id)
    cols = list(df.columns)
    log_code = []
    
    for action, ids in payload.plan.items():
        for cid in ids:
            if 1 <= cid <= len(cols):
                col = cols[cid-1]
                
                # Check categorical conversion for mean/median
                is_cat = is_object_dtype(df[col])
                if action in ['mean', 'median'] and is_cat:
                    try:
                        df[col] = pd.to_numeric(df[col], errors='raise')
                        log_code.append(f"df['{col}'] = pd.to_numeric(df['{col}'], errors='raise')")
                    except:
                        continue # Skip if conversion fails
                
                if action == 'mean':
                    val = df[col].mean()
                    df[col].fillna(val, inplace=True)
                    log_code.append(f"df['{col}'].fillna({val:.2f}, inplace=True)")
                elif action == 'median':
                    val = df[col].median()
                    df[col].fillna(val, inplace=True)
                    log_code.append(f"df['{col}'].fillna({val:.2f}, inplace=True)")
                elif action == 'mode':
                    if not df[col].mode().empty:
                        val = df[col].mode()[0]
                        df[col].fillna(val, inplace=True)
                        log_code.append(f"df['{col}'].fillna('{val}', inplace=True)")
                elif action == 'drop_col':
                    df.drop(columns=[col], inplace=True)
                    log_code.append(f"df.drop(columns=['{col}'], inplace=True)")

    save_df(payload.session_id, df)
    if log_code:
        update_mongo_logs(payload.session_id, "Handle Missing Values", log_code)
        
    return {"message": "Missing values handled", "columns": get_df_info_dict(df)}

# --- 4. OUTLIERS ---
@app.get("/suggestions/outliers/{session_id}")
def suggest_outliers(session_id: str):
    df = load_df(session_id)
    nums = df.select_dtypes(include=np.number).columns
    suggestions = {}
    
    for col in nums:
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        cnt = ((df[col] < (Q1 - 1.5*IQR)) | (df[col] > (Q3 + 1.5*IQR))).sum()
        pct = (cnt / len(df)) * 100
        
        if cnt > 0:
            col_id = df.columns.get_loc(col) + 1
            action = 'remove_rows' if pct > 10 else 'cap'
            suggestions[col_id] = {
                "column": col, "outliers_pct": round(pct, 2), "suggested_action": action
            }
            
    return suggestions

@app.post("/clean/outliers")
def apply_outlier_plan(payload: OutlierPlan):
    df = load_df(payload.session_id)
    cols = list(df.columns)
    log_code = []
    
    for action, ids in payload.plan.items():
        for cid in ids:
            if 1 <= cid <= len(cols):
                col = cols[cid-1]
                if not pd.api.types.is_numeric_dtype(df[col]): continue
                
                Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
                
                if action == 'cap':
                    df[col] = df[col].clip(lower=lower, upper=upper)
                    log_code.append(f"# Cap {col}\nQ1,Q3=df['{col}'].quantile([0.25,0.75])\nIQR=Q3-Q1\ndf['{col}']=df['{col}'].clip(Q1-1.5*IQR, Q3+1.5*IQR)")
                elif action == 'remove_rows':
                    df = df[(df[col] >= lower) & (df[col] <= upper)]
                    log_code.append(f"# Remove Rows {col}\nQ1,Q3=df['{col}'].quantile([0.25,0.75])\nIQR=Q3-Q1\ndf=df[(df['{col}']>=Q1-1.5*IQR)&(df['{col}']<=Q3+1.5*IQR)]")

    save_df(payload.session_id, df)
    if log_code:
        update_mongo_logs(payload.session_id, "Handle Outliers", log_code)
        
    return {"message": "Outliers handled", "shape": df.shape}

# --- 5. CORRELATION ---
@app.post("/clean/correlation")
def handle_correlation(payload: CorrelationPlan):
    df = load_df(payload.session_id)
    nums = df.select_dtypes(include=np.number).columns
    log_code = []
    
    corr_matrix = df[nums].corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    
    high_corr_cols = [column for column in upper.columns if any(upper[column] > payload.threshold)]
    
    # If just checking or auto-dropping
    if payload.auto_drop:
        if high_corr_cols:
            df.drop(columns=high_corr_cols, inplace=True)
            log_code.append(f"# Drop High Correlation > {payload.threshold}\ndf.drop(columns={high_corr_cols}, inplace=True)")
            save_df(payload.session_id, df)
            update_mongo_logs(payload.session_id, "Handle Correlation", log_code)
        return {"message": f"Auto-dropped {len(high_corr_cols)} columns", "dropped": high_corr_cols}
        
    # If applying specific plan
    if payload.plan:
        cols_to_drop = []
        # payload.plan['drop'] contains IDs
        current_cols = list(df.columns)
        if 'drop' in payload.plan:
            for cid in payload.plan['drop']:
                if 1 <= cid <= len(current_cols):
                    cols_to_drop.append(current_cols[cid-1])
        
        if cols_to_drop:
            df.drop(columns=cols_to_drop, inplace=True)
            log_code.append(f"df.drop(columns={cols_to_drop}, inplace=True)")
            save_df(payload.session_id, df)
            update_mongo_logs(payload.session_id, "Handle Correlation (Manual)", log_code)
            return {"message": "Dropped specific correlated columns", "dropped": cols_to_drop}

    # If no plan, return detected issues
    return {"message": "Detected high correlation", "columns_to_drop": high_corr_cols}

# --- 6. ENCODING ---
@app.get("/suggestions/encoding/{session_id}")
def suggest_encoding(session_id: str):
    df = load_df(session_id)
    cats = df.select_dtypes(include=['object', 'category']).columns
    suggestions = {}
    for col in cats:
        col_id = df.columns.get_loc(col) + 1
        unique = df[col].nunique()
        action = 'one_hot' if unique <= 10 else 'label'
        suggestions[col_id] = {"column": col, "unique": unique, "suggested_action": action}
    return suggestions

@app.post("/clean/encoding")
def apply_encoding(payload: EncodingPlan):
    df = load_df(payload.session_id)
    cols = list(df.columns)
    log_code = []
    
    # Label Encoding
    if 'label' in payload.plan:
        for cid in payload.plan['label']:
            col = cols[cid-1]
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            log_code.append(f"le=LabelEncoder(); df['{col}']=le.fit_transform(df['{col}'].astype(str))")
            
    # One Hot
    if 'one_hot' in payload.plan:
        oh_cols = [cols[cid-1] for cid in payload.plan['one_hot'] if 1 <= cid <= len(cols)]
        if oh_cols:
            df = pd.get_dummies(df, columns=oh_cols, drop_first=True)
            log_code.append(f"df=pd.get_dummies(df, columns={oh_cols}, drop_first=True)")
            
    save_df(payload.session_id, df)
    if log_code:
        update_mongo_logs(payload.session_id, "Categorical Encoding", log_code)
        
    return {"message": "Encoding complete", "columns": get_df_info_dict(df)}

# --- 7. SCALING ---
@app.get("/suggestions/scaling/{session_id}")
def suggest_scaling(session_id: str):
    df = load_df(session_id)
    nums = df.select_dtypes(include=np.number).columns
    suggestions = {}
    for col in nums:
        if df[col].nunique() < 3: continue # Skip binary
        col_id = df.columns.get_loc(col) + 1
        skew = df[col].skew()
        action = 'standard' if abs(skew) < 1 else 'minmax'
        suggestions[col_id] = {"column": col, "skew": round(skew,2), "suggested_action": action}
    return suggestions

@app.post("/clean/scaling")
def apply_scaling(payload: ScalingPlan):
    df = load_df(payload.session_id)
    cols = list(df.columns)
    log_code = []
    
    # Standard
    if 'standard' in payload.plan:
        std_cols = [cols[cid-1] for cid in payload.plan['standard'] if 1 <= cid <= len(cols)]
        if std_cols:
            scaler = StandardScaler()
            df[std_cols] = scaler.fit_transform(df[std_cols])
            log_code.append(f"scaler=StandardScaler(); df[{std_cols}]=scaler.fit_transform(df[{std_cols}])")
            
    # MinMax
    if 'minmax' in payload.plan:
        mm_cols = [cols[cid-1] for cid in payload.plan['minmax'] if 1 <= cid <= len(cols)]
        if mm_cols:
            scaler = MinMaxScaler()
            df[mm_cols] = scaler.fit_transform(df[mm_cols])
            log_code.append(f"scaler=MinMaxScaler(); df[{mm_cols}]=scaler.fit_transform(df[{mm_cols}])")
            
    save_df(payload.session_id, df)
    if log_code:
        update_mongo_logs(payload.session_id, "Feature Scaling", log_code)
        
    return {"message": "Scaling complete"}

# --- 8. ANALYSIS ---
@app.get("/analysis/univariate/{session_id}")
def get_univariate_stats(session_id: str):
    df = load_df(session_id)
    nums = df.select_dtypes(include=np.number).columns
    
    # Log generic code
    nb_code = [
        "numeric_cols = df.select_dtypes(include=np.number).columns",
        "for col in numeric_cols:",
        "    fig, ax = plt.subplots(1, 2, figsize=(14, 5))",
        "    sns.histplot(df[col], kde=True, ax=ax[0])",
        "    sns.boxplot(x=df[col], ax=ax[1])",
        "    plt.show()"
    ]
    update_mongo_logs(session_id, "Univariate Analysis", nb_code)
    
    stats = df[nums].describe().T
    stats['skew'] = df[nums].skew()
    return stats.to_dict(orient="index")

@app.get("/analysis/bivariate/{session_id}")
def get_bivariate_corr(session_id: str):
    df = load_df(session_id)
    nums = df.select_dtypes(include=np.number).columns
    
    # Log generic code
    nb_code = [
        "numeric_cols = df.select_dtypes(include=np.number).columns",
        "sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm')",
        "plt.show()",
        "sns.pairplot(df[numeric_cols])",
        "plt.show()"
    ]
    update_mongo_logs(session_id, "Bivariate Analysis", nb_code)
    
    corr = df[nums].corr()
    return corr.to_dict()

# --- 9. NOTEBOOK GENERATION ---
@app.post("/download/notebook")
def download_notebook(session_id: str = Body(..., embed=True), filename: str = Body("workflow", embed=True)):
    session = sessions_col.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    logs = session.get("logs", [])
    
    notebook = {
        "cells": [],
        "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"}},
        "nbformat": 4, "nbformat_minor": 4
    }
    
    # Imports Cell
    notebook["cells"].append({
        "cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
        "source": ["import pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nfrom sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder\n%matplotlib inline\nimport warnings\nwarnings.filterwarnings('ignore')\n"]
    })
    
    for entry in logs:
        notebook["cells"].append({"cell_type": "markdown", "metadata": {}, "source": [f"### {entry['step']}"]})
        notebook["cells"].append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], 
                                  "source": [l + "\n" for l in entry['code']]})
                                  
    out_file = f"{filename}_{session_id}.ipynb"
    with open(out_file, 'w') as f:
        json.dump(notebook, f, indent=4)
        
    return FileResponse(out_file, filename=f"{filename}.ipynb", media_type="application/x-ipynb+json")

@app.get("/download/csv/{session_id}")
def download_csv(session_id: str):
    path = get_session_file_path(session_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404)
        
    # Convert parquet back to csv for download
    df = pd.read_parquet(path)
    out_path = f"temp_{session_id}.csv"
    df.to_csv(out_path, index=False)
    
    return FileResponse(out_path, filename="clean_data.csv", media_type="text/csv")

if __name__ == "__main__":
    import uvicorn
    print("Starting AutoEDA API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)