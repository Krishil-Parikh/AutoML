import pandas as pd
import numpy as np
from pandas.api.types import is_object_dtype, is_categorical_dtype  # For cleaner checks
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
import json
import os
import scipy.stats as stats
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# ==========================================
# 1. NOTEBOOK GENERATOR FUNCTION
# ==========================================
def save_to_ipynb(log_steps, filename="preprocessing_workflow.ipynb"):
    """
    Saves the recorded workflow steps into a .ipynb file.
    """
    if not filename.endswith('.ipynb'):
        filename += '.ipynb'
        
    # Create the notebook structure
    notebook = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.5"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    # Helper to create a code cell
    def create_code_cell(source_lines):
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in source_lines]
        }

    # Helper to create markdown cell
    def create_markdown_cell(text):
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": [text]
        }

    # Add Import Cell
    imports = [
        "import pandas as pd",
        "import numpy as np",
        "import matplotlib.pyplot as plt",
        "import seaborn as sns",
        "from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder",
        "%matplotlib inline",
        "import warnings",
        "warnings.filterwarnings('ignore')"
    ]
    notebook["cells"].append(create_code_cell(imports))

    # Add User Steps
    for step_name, code_lines in log_steps:
        # Add a markdown header for the step
        notebook["cells"].append(create_markdown_cell(f"### {step_name}"))
        # Add the code
        notebook["cells"].append(create_code_cell(code_lines))

    try:
        with open(filename, 'w') as f:
            json.dump(notebook, f, indent=4)
        print(f"\nSuccessfully generated notebook: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"Error saving notebook: {e}")

# ==========================================
# 2. DATA LOADING
# ==========================================
def load_csv_to_dataframe(log_list=None):
    file_path = r"C:\Users\krish\Downloads\daily_weather (1).csv"
    try:
        df = pd.read_csv(file_path)
        print("\nCSV loaded successfully!")
        print(f"Shape: {df.shape}")
        print("\nFirst 5 rows:\n")
        print(df.head())
        
        # LOGGING
        if log_list is not None:
            log_list.append(("Load Data", [
                f"file_path = r'{file_path}'",
                "df = pd.read_csv(file_path)",
                "print(f'Shape: {{df.shape}}')",
                "df.head()"
            ]))
            
        return df
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_df_info(df):
    unique_percentages = (df.nunique() / len(df)) * 100
    missing_percentages = (df.isnull().sum() / len(df)) * 100
    dtypes = df.dtypes
    
    df_info = pd.DataFrame({
        'id': range(1, len(df.columns) + 1),
        'column_name': df.columns,
        'dtype': dtypes.values,
        'percentage_unique': unique_percentages.values,
        'percentage_missing': missing_percentages.values
    })
    
    df_info['percentage_unique'] = df_info['percentage_unique'].round(2)
    df_info['percentage_missing'] = df_info['percentage_missing'].round(2)
    
    return df_info

# ==========================================
# 3. DROP COLUMNS
# ==========================================
def drop_columns_by_id(df, df_info, log_list=None):
    if df_info is None or df_info.empty:
        print("No column info available. Cannot drop columns.")
        return df
    
    print("\nAvailable columns:")
    print(df_info[['id', 'column_name', 'dtype', 'percentage_unique', 'percentage_missing']])
    
    user_input = input("\nEnter IDs to drop (e.g., '1, 2, 3, 5-8, 9') or 'none' to skip: ").strip()
    
    if user_input.lower() == 'none':
        print("No columns dropped.")
        return df
    
    ids_to_drop = set()
    parts = [part.strip() for part in user_input.split(',')]
    
    for part in parts:
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                if start > end:
                    print(f"Warning: Invalid range '{part}' (start > end). Skipping.")
                    continue
                ids_to_drop.update(range(start, end + 1))
            except ValueError:
                print(f"Warning: Invalid range '{part}'. Skipping.")
        else:
            try:
                ids_to_drop.add(int(part))
            except ValueError:
                print(f"Warning: Invalid ID '{part}'. Skipping.")
    
    valid_ids = {i for i in ids_to_drop if 1 <= i <= len(df_info)}
    invalid_ids = ids_to_drop - valid_ids
    
    if invalid_ids:
        print(f"Warning: Invalid IDs out of range: {sorted(invalid_ids)}. Skipping them.")
    
    if not valid_ids:
        print("No valid IDs to drop.")
        return df
    
    columns_to_drop = df_info[df_info['id'].isin(valid_ids)]['column_name'].tolist()
    print(f"Dropping columns: {columns_to_drop}")
    df_updated = df.drop(columns=columns_to_drop)
    print(f"Updated DataFrame shape: {df_updated.shape}")
    
    # LOGGING
    if log_list is not None:
        log_list.append(("Drop Columns", [
            f"columns_to_drop = {columns_to_drop}",
            "df.drop(columns=columns_to_drop, inplace=True)",
            "print(f'Dropped columns: {columns_to_drop}')"
        ]))

    return df_updated

# ==========================================
# 4. MISSING VALUES
# ==========================================
def generate_global_suggestion(df, df_info, missing_cols):
    suggestions = {}
    
    for _, row in missing_cols.iterrows():
        col_name = row['column_name']
        col_id = row['id']
        dtype = row['dtype']
        missing_pct = row['percentage_missing']
        col_data = df[col_name].dropna()
        
        if missing_pct > 50:
            suggestions[col_id] = 'drop_col'
        elif is_object_dtype(dtype) or isinstance(dtype, pd.CategoricalDtype):
            suggestions[col_id] = 'mode'
        else:
            skew = col_data.skew() if len(col_data) > 0 else 0
            if abs(skew) > 1:
                suggestions[col_id] = 'median'
            else:
                suggestions[col_id] = 'mean'
    
    return suggestions

def parse_user_plan(user_input):
    plan = {'mean': set(), 'median': set(), 'mode': set(), 'drop_col': set()}
    
    if not user_input.strip():
        return plan
    
    parts = [p.strip() for p in user_input.split(';') if p.strip()]
    
    for part in parts:
        if part.startswith('mean'):
            action = 'mean'
        elif part.startswith('median'):
            action = 'median'
        elif part.startswith('mode'):
            action = 'mode'
        elif part.startswith('drop'):
            action = 'drop_col'
        else:
            print(f"Warning: Could not parse part '{part}'. Skipping.")
            continue
        
        if '-' not in part:
            print(f"Warning: No IDs found after dash in '{part}'. Skipping.")
            continue
        
        id_part = part.split('-', 1)[1].strip()
        ids = set()
        
        for sub in [s.strip() for s in id_part.split(',')]:
            if '-' in sub:
                try:
                    start, end = map(int, sub.split('-'))
                    ids.update(range(start, end + 1))
                except:
                    print(f"Invalid range '{sub}'. Skipping.")
            else:
                try:
                    ids.add(int(sub))
                except:
                    print(f"Invalid ID '{sub}'. Skipping.")
        
        plan[action].update(ids)
    
    return plan

def handle_missing_values(df, df_info, log_list=None):
    missing_cols = df_info[df_info['percentage_missing'] > 0].copy()
    
    if missing_cols.empty:
        print("No missing values found in the DataFrame.")
        return df, df_info
    
    print("\nColumns with missing values:")
    print(missing_cols[['id', 'column_name', 'dtype', 'percentage_missing']])
    
    global_suggestion = generate_global_suggestion(df, df_info, missing_cols)
    
    print("\n=== GLOBAL SUGGESTION FOR MISSING VALUES ===")
    for col_id, action in global_suggestion.items():
        col_name = df_info[df_info['id'] == col_id]['column_name'].iloc[0]
        print(f"ID {col_id} ({col_name}): {action}")
    
    approve = input("\nDo you approve this global suggestion? (y/n): ").strip().lower()
    
    updated_df = df.copy()
    updated_info = df_info.copy()
    
    if approve == 'y':
        user_plan = {}
        for col_id, action in global_suggestion.items():
            user_plan.setdefault(action, set()).add(col_id)
    else:
        print("\nPlease provide your custom plan in the following format:")
        print("mean -1,2,3 ; median -4,5-7 ; mode-8,9 ; drop -10,11-13;")
        user_input = input("Your plan: ").strip()
        user_plan = parse_user_plan(user_input)
    
    # Covered and uncovered
    covered_ids = set()
    for ids in user_plan.values():
        covered_ids.update(ids)
    
    all_missing_ids = set(missing_cols['id'])
    uncovered_ids = all_missing_ids - covered_ids
    
    # Logging container
    log_code = []

    # Inner function to apply actions and log them
    def apply_actions(plan, target_ids, current_df, current_info):
        for action, col_ids in plan.items():
            valid_ids = [cid for cid in col_ids if cid in target_ids]
            for col_id in valid_ids:
                col_name = current_info[current_info['id'] == col_id]['column_name'].iloc[0]
                dtype = current_info[current_info['id'] == col_id]['dtype'].iloc[0]
                is_categorical = is_object_dtype(dtype) or isinstance(dtype, pd.CategoricalDtype)
                
                print(f"\nApplying '{action}' to ID {col_id} ({col_name})")
                
                if action in ['mean', 'median'] and is_categorical:
                    print(f"⚠️  WARNING: '{action}' requested on categorical column '{col_name}' (dtype={dtype})")
                    convert = input("Attempt to convert to numeric? (y/n): ").strip().lower()
                    if convert == 'y':
                        try:
                            current_df[col_name] = pd.to_numeric(current_df[col_name], errors='raise')
                            print(f"Converted '{col_name}' to numeric.")
                            current_info.loc[current_info['column_name'] == col_name, 'dtype'] = current_df[col_name].dtype
                            log_code.append(f"df['{col_name}'] = pd.to_numeric(df['{col_name}'], errors='raise')")
                        except:
                            print("Conversion failed. Skipping this column.")
                            continue
                    else:
                        print("Skipping this column.")
                        continue
                
                if action == 'mean':
                    val = current_df[col_name].mean()
                    if not np.isnan(val):
                        current_df[col_name] = current_df[col_name].fillna(val)
                        print(f"Filled with mean: {val:.2f}")
                        log_code.append(f"df['{col_name}'].fillna(df['{col_name}'].mean(), inplace=True)")
                
                elif action == 'median':
                    val = current_df[col_name].median()
                    if not np.isnan(val):
                        current_df[col_name] = current_df[col_name].fillna(val)
                        print(f"Filled with median: {val:.2f}")
                        log_code.append(f"df['{col_name}'].fillna(df['{col_name}'].median(), inplace=True)")
                
                elif action == 'mode':
                    mode_val = current_df[col_name].mode()
                    if not mode_val.empty:
                        current_df[col_name] = current_df[col_name].fillna(mode_val.iloc[0])
                        print(f"Filled with mode: {mode_val.iloc[0]}")
                        log_code.append(f"df['{col_name}'].fillna(df['{col_name}'].mode()[0], inplace=True)")
                
                elif action == 'drop_col':
                    current_df.drop(columns=[col_name], inplace=True)
                    current_info = current_info[current_info['id'] != col_id].reset_index(drop=True)
                    # Note: Re-indexing of ID happens later in valid flow, preserving original logic
                    print(f"Dropped column '{col_name}'")
                    log_code.append(f"df.drop(columns=['{col_name}'], inplace=True)")

    # Apply user's plan first (on mentioned columns)
    apply_actions(user_plan, all_missing_ids, updated_df, updated_info)
    
    # Handle uncovered columns
    if uncovered_ids:
        print(f"\n⚠️  The following columns with missing values were NOT mentioned in your plan:")
        print(missing_cols[missing_cols['id'].isin(uncovered_ids)][['id', 'column_name', 'percentage_missing']])
        
        while True:
            choice = input("\nWhat do you want to do for these columns?\n"
                           "1: Provide custom actions now\n"
                           "2: Apply my original global suggestions\n"
                           "3: Do nothing (leave missing values as-is)\n"
                           "Enter 1, 2, or 3: ").strip()
            
            if choice == '1':
                print("\nProvide additional plan for these columns (same format):")
                extra_input = input("Additional plan: ").strip()
                extra_plan = parse_user_plan(extra_input)
                apply_actions(extra_plan, uncovered_ids, updated_df, updated_info)
                # Recalculate covered
                for ids in extra_plan.values(): covered_ids.update(ids)
                remaining = uncovered_ids - covered_ids
                if not remaining: break
                
            elif choice == '2':
                print("Applying original global suggestions to uncovered columns...")
                temp_plan = {}
                for col_id in uncovered_ids:
                    act = global_suggestion.get(col_id, 'median')
                    temp_plan.setdefault(act, set()).add(col_id)
                apply_actions(temp_plan, uncovered_ids, updated_df, updated_info)
                break
            
            elif choice == '3':
                print("Leaving missing values untouched in uncovered columns.")
                break
            
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
    
    # Final missing % update
    new_missing = (updated_df.isnull().sum() / len(updated_df)) * 100
    # Refresh info to handle drops
    cols_present = updated_df.columns
    updated_info = updated_info[updated_info['column_name'].isin(cols_present)].reset_index(drop=True)
    updated_info['id'] = range(1, len(updated_info) + 1)
    
    for col_name in updated_df.columns:
        if col_name in updated_info['column_name'].values:
            updated_info.loc[updated_info['column_name'] == col_name, 'percentage_missing'] = round(new_missing[col_name], 2)
    
    print(f"\nMissing value handling complete. Final shape: {updated_df.shape}")
    
    # LOGGING
    if log_list is not None and log_code:
        log_list.append(("Handle Missing Values", log_code))

    return updated_df, updated_info

# ==========================================
# 5. OUTLIERS
# ==========================================
def parse_outlier_plan(user_input):
    """
    Parse plan like: cap -1,2,3 ; remove_rows -4-6 ; none -7,8 ;
    Returns dict: {'cap': set(), 'remove_rows': set(), 'none': set()}
    """
    plan = {'cap': set(), 'remove_rows': set(), 'none': set()}
    
    if not user_input.strip():
        return plan
    
    parts = [p.strip() for p in user_input.split(';') if p.strip()]
    
    for part in parts:
        action = None
        if part.startswith('cap'):
            action = 'cap'
        elif part.startswith('remove_rows'):
            action = 'remove_rows'
        elif part.startswith('none'):
            action = 'none'
        else:
            print(f"Warning: Unknown action in '{part}'. Skipping.")
            continue
        
        if '-' not in part:
            print(f"Warning: No IDs found in '{part}'. Skipping.")
            continue
        
        id_part = part.split('-', 1)[1].strip()
        ids = set()
        
        for sub in [s.strip() for s in id_part.split(',')]:
            if '-' in sub:
                try:
                    start, end = map(int, sub.split('-'))
                    ids.update(range(start, end + 1))
                except:
                    print(f"Invalid range '{sub}'. Skipping.")
            else:
                try:
                    ids.add(int(sub))
                except:
                    print(f"Invalid ID '{sub}'. Skipping.")
        
        plan[action].update(ids)
    
    return plan

def detect_and_handle_outliers(df, df_info, log_list=None):
    """
    Interactive outlier detection & handling — same flow as missing values.
    """
    # Identify numeric columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) == 0:
        print("No numeric columns found for outlier detection.")
        return df, df_info
    
    print("\n=== OUTLIER DETECTION (IQR Method) ===")
    print("Analyzing numeric columns for outliers...\n")
    
    outlier_summary = []
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers_count = df[(df[col] < lower_bound) | (df[col] > upper_bound)].shape[0]
        outliers_pct = (outliers_count / len(df)) * 100
        
        if outliers_count > 0:
            outlier_summary.append({
                'column_name': col,
                'outliers_count': outliers_count,
                'outliers_pct': round(outliers_pct, 2),
                'lower_bound': round(lower_bound, 2),
                'upper_bound': round(upper_bound, 2)
            })
    
    if not outlier_summary:
        print("No outliers detected in any numeric column using IQR method. Great!")
        return df, df_info
    
    # Create summary DataFrame
    outlier_df = pd.DataFrame(outlier_summary).sort_values('outliers_pct', ascending=False)
    
    print("Columns with detected outliers:")
    print(outlier_df.to_string(index=False))
    
    # Map to original IDs
    outlier_cols_info = df_info[df_info['column_name'].isin(outlier_df['column_name'])].copy()
    outlier_cols_info = outlier_cols_info[['id', 'column_name']].merge(
        outlier_df[['column_name', 'outliers_count', 'outliers_pct', 'lower_bound', 'upper_bound']],
        on='column_name'
    ).sort_values('outliers_pct', ascending=False).reset_index(drop=True)
    
    print("\nColumns with outliers (use these IDs for your plan):")
    print(outlier_cols_info[['id', 'column_name', 'outliers_count', 'outliers_pct']])
    
    # === GLOBAL SUGGESTION ===
    global_suggestion = {}
    for _, row in outlier_cols_info.iterrows():
        col_id = row['id']
        col_name = row['column_name']
        pct = row['outliers_pct']
        
        if pct > 10:  # Heavy outliers → suggest remove_rows
            global_suggestion[col_id] = 'remove_rows'
        elif 'rain' in col_name.lower():  # Rain features → cap (extreme rain is real)
            global_suggestion[col_id] = 'cap'
        else:  # Default for most weather features
            global_suggestion[col_id] = 'cap'
    
    print("\n=== GLOBAL SUGGESTION FOR OUTLIERS ===")
    for col_id, action in global_suggestion.items():
        col_name = outlier_cols_info[outlier_cols_info['id'] == col_id]['column_name'].iloc[0]
        pct = outlier_cols_info[outlier_cols_info['id'] == col_id]['outliers_pct'].iloc[0]
        print(f"ID {col_id} ({col_name}): {action} (outliers: {pct}%)")
    
    approve = input("\nDo you approve this global suggestion? (y/n): ").strip().lower()
    
    updated_df = df.copy()
    updated_info = df_info.copy()
    
    if approve == 'y':
        user_plan = {}
        for col_id, action in global_suggestion.items():
            user_plan.setdefault(action, set()).add(col_id)
    else:
        print("\nProvide your custom plan in this format:")
        print("cap -1,2,3 ; remove_rows -4-6 ; none -7,8 ;")
        user_input = input("Your plan: ").strip()
        user_plan = parse_outlier_plan(user_input)
    
    # === Covered / Uncovered ===
    covered_ids = set()
    for ids in user_plan.values():
        covered_ids.update(ids)
    
    all_outlier_ids = set(outlier_cols_info['id'])
    uncovered_ids = all_outlier_ids - covered_ids
    
    # Logging Container
    log_code = []

    def apply_outlier_logic(plan, target_ids, current_df):
        for action, col_ids in plan.items():
            valid_ids = [cid for cid in col_ids if cid in target_ids]
            for col_id in valid_ids:
                col_name = updated_info[updated_info['id'] == col_id]['column_name'].iloc[0]
                bounds = outlier_cols_info[outlier_cols_info['id'] == col_id][['lower_bound', 'upper_bound']].iloc[0]
                lower, upper = bounds['lower_bound'], bounds['upper_bound']
                
                print(f"\nApplying '{action}' to ID {col_id} ({col_name})")
                
                if action == 'cap':
                    current_df[col_name] = current_df[col_name].clip(lower=lower, upper=upper)
                    print(f"  Capped to [{lower}, {upper}]")
                    # Log
                    log_code.append(f"# Cap Outliers: {col_name}")
                    log_code.append(f"Q1 = df['{col_name}'].quantile(0.25)")
                    log_code.append(f"Q3 = df['{col_name}'].quantile(0.75)")
                    log_code.append(f"IQR = Q3 - Q1")
                    log_code.append(f"df['{col_name}'] = df['{col_name}'].clip(lower=Q1-1.5*IQR, upper=Q3+1.5*IQR)")
                    
                elif action == 'remove_rows':
                    initial_rows = len(current_df)
                    mask = (current_df[col_name] >= lower) & (current_df[col_name] <= upper)
                    current_df = current_df[mask].reset_index(drop=True)
                    removed = initial_rows - len(current_df)
                    print(f"  Removed {removed} rows with outliers in '{col_name}'")
                    # Log
                    log_code.append(f"# Remove Rows Outliers: {col_name}")
                    log_code.append(f"Q1 = df['{col_name}'].quantile(0.25)")
                    log_code.append(f"Q3 = df['{col_name}'].quantile(0.75)")
                    log_code.append(f"IQR = Q3 - Q1")
                    log_code.append(f"df = df[(df['{col_name}'] >= Q1-1.5*IQR) & (df['{col_name}'] <= Q3+1.5*IQR)]")
                    
                elif action == 'none':
                    print("  No action taken.")
        return current_df

    # Apply user's plan
    updated_df = apply_outlier_logic(user_plan, all_outlier_ids, updated_df)
    
    # === Handle uncovered columns (if any) ===
    if uncovered_ids:
        print(f"\n⚠️  The following columns with outliers were NOT mentioned:")
        print(outlier_cols_info[outlier_cols_info['id'].isin(uncovered_ids)][['id', 'column_name', 'outliers_pct']])
        
        while True:
            choice = input("\nWhat to do with these columns?\n"
                           "1: Provide custom actions now\n"
                           "2: Apply my original global suggestions\n"
                           "3: Do nothing (leave outliers as-is)\n"
                           "Enter 1, 2, or 3: ").strip()
            
            if choice == '1':
                print("\nProvide additional plan for these columns:")
                extra_input = input("Additional plan: ").strip()
                extra_plan = parse_outlier_plan(extra_input)
                updated_df = apply_outlier_logic(extra_plan, uncovered_ids, updated_df)
                break
            
            elif choice == '2':
                print("Applying original global suggestions to uncovered columns...")
                temp_plan = {}
                for col_id in uncovered_ids:
                    act = global_suggestion.get(col_id, 'cap')
                    temp_plan.setdefault(act, set()).add(col_id)
                updated_df = apply_outlier_logic(temp_plan, uncovered_ids, updated_df)
                break
            
            elif choice == '3':
                print("Leaving outliers untouched in uncovered columns.")
                break
            
            else:
                print("Invalid choice. Try again.")
    
    print(f"\nOutlier handling complete. Final shape: {updated_df.shape}")
    updated_info = get_df_info(updated_df)
    
    # LOGGING
    if log_list is not None and log_code:
        log_list.append(("Handle Outliers", log_code))
        
    return updated_df, updated_info

# ==========================================
# 6. UNIVARIATE ANALYSIS
# ==========================================
def univariate_analysis(df, df_info, log_list=None):
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) == 0:
        print("No numeric columns available for univariate analysis.")
        return
    
    print("\n=== UNIVARIATE ANALYSIS ===")
    print("Key descriptive statistics for numeric columns:\n")
    
    stats = df[numeric_cols].describe().T
    stats['skew'] = df[numeric_cols].skew().round(2)
    stats['%_zeros'] = (df[numeric_cols] == 0).mean().round(4) * 100
    stats = stats[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max', 'skew', '%_zeros']]
    print(stats.to_string())
    
    # LOGGING - Add generic code for univariate
    if log_list is not None:
        nb_code = [
            "numeric_cols = df.select_dtypes(include=np.number).columns",
            "for col in numeric_cols:",
            "    fig, ax = plt.subplots(1, 2, figsize=(14, 5))",
            "    sns.histplot(df[col], kde=True, ax=ax[0])",
            "    ax[0].set_title(f'Dist of {col}')",
            "    sns.boxplot(x=df[col], ax=ax[1])",
            "    ax[1].set_title(f'Boxplot of {col}')",
            "    plt.show()"
        ]
        log_list.append(("Univariate Analysis", nb_code))
    
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        import scipy.stats as stats
        import warnings
        warnings.filterwarnings("ignore", category=FutureWarning)
        
        # Plot type selection
        print("\n" + "="*60)
        print("CHOOSE PLOT TYPES (you can select multiple)")
        print("="*60)
        print("1: Basic Plots Only (Histogram + Boxplot)")
        print("2: Histogram with KDE + Stats Overlay")
        print("3: Boxplot + Swarmplot")
        print("4: Violin Plot")
        print("5: QQ Plot")
        print("6: All of the above")
        print("Example: 1,3,5   or   2-4   or   6")
        
        attempts = 0
        selected_plots = set()
        while attempts < 3:
            user_input = input("\nYour choice: ").strip()
            if not user_input:
                attempts += 1
                print("Empty input not allowed.")
                continue
            
            temp_set = set()
            parts = [p.strip() for p in user_input.replace(' ', '').split(',')]
            valid = True
            for part in parts:
                if '-' in part:
                    try:
                        start, end = map(int, part.split('-'))
                        if 1 <= start <= end <= 6:
                            temp_set.update(range(start, end + 1))
                        else:
                            valid = False
                    except:
                        valid = False
                else:
                    try:
                        val = int(part)
                        if 1 <= val <= 6:
                            temp_set.add(val)
                        else:
                            valid = False
                    except:
                        valid = False
            
            if valid and temp_set:
                selected_plots = temp_set
                break
            else:
                attempts += 1
                print(f"Invalid selection. {3 - attempts} attempts left.")
        
        if not selected_plots:
            print("Too many invalid attempts. Defaulting to Basic Plots (1).")
            selected_plots = {1}
        
        if 6 in selected_plots:
            selected_plots = {1, 2, 3, 4, 5}
        
        print(f"\nSelected plot types: {sorted(selected_plots)}")
        
        # Figure size
        print("\nChoose figure size:")
        print("1: Small (12x6)   2: Medium (16x8) - Recommended   3: Large (20x10)   4: Custom")
        size_choice = input("Enter choice (1-4): ").strip() or '2'
        if size_choice == '1':
            base_w, base_h = 12, 6
        elif size_choice == '3':
            base_w, base_h = 20, 10
        elif size_choice == '4':
            custom = input("Enter width,height (e.g., 18,10): ").strip()
            try:
                base_w, base_h = map(float, custom.split(','))
            except:
                base_w, base_h = 16, 8
        else:
            base_w, base_h = 16, 8
        
        # Save folder
        folder = input("\nSave folder (Enter = current directory): ").strip() or "."
        import os
        os.makedirs(folder, exist_ok=True)
        print(f"All plots will be saved to: {os.path.abspath(folder)}")
        
        # Viewing & Saving mode
        print("\n" + "="*50)
        print("VIEWING & SAVING MODE")
        print("="*50)
        print("1: View all plots one by one → save ALL at the end")
        print("2: Directly save all plots (no viewing)")
        print("3: View each plot → decide save individually")
        mode_input = input("Choose mode (1/2/3): ").strip() or '1'
        mode = mode_input if mode_input in ['1', '2', '3'] else '1'
        
        figures_to_save = []
        
        for col in numeric_cols:
            print(f"\nGenerating univariate plots for: {col}")
            
            mean_val = df[col].mean()
            median_val = df[col].median()
            skew_val = df[col].skew()
            zero_pct = (df[col] == 0).mean() * 100
            
            # For option 1 (Basic), it always creates 2 subplots
            effective_num_plots = len(selected_plots)
            if 1 in selected_plots:
                effective_num_plots = max(effective_num_plots, 2)  # Force 2 for basic
            
            cols_per_row = min(effective_num_plots, 3)
            rows = (effective_num_plots + cols_per_row - 1) // cols_per_row
            
            fig_width = base_w * cols_per_row
            fig_height = base_h * rows
            
            fig, axes = plt.subplots(rows, cols_per_row, figsize=(fig_width, fig_height))
            
            # Robust axes handling
            if rows == 1 and cols_per_row == 1:
                axes = [axes]
            elif rows == 1:
                axes = list(axes)
            else:
                axes = axes.flatten().tolist()
            
            ax_idx = 0
            
            if 1 in selected_plots:
                # Histogram
                ax = axes[ax_idx]
                df[col].hist(bins=50, ax=ax, color='skyblue', edgecolor='black', alpha=0.8)
                ax.set_title('Histogram')
                ax.set_xlabel(col)
                ax.set_ylabel('Frequency')
                ax.grid(alpha=0.3)
                ax_idx += 1
                
                # Boxplot
                ax = axes[ax_idx]
                df.boxplot(column=col, ax=ax, patch_artist=True,
                           boxprops=dict(facecolor='lightcoral'), medianprops=dict(color='black'))
                ax.set_title('Boxplot')
                ax.grid(alpha=0.3)
                ax_idx += 1
            
            if 2 in selected_plots:
                ax = axes[ax_idx]
                df[col].hist(bins=50, ax=ax, color='lightblue', alpha=0.7, density=True)
                df[col].plot.density(ax=ax, color='red', linewidth=2, label='KDE')
                ax.axvline(mean_val, color='green', linestyle='--', label=f'Mean: {mean_val:.2f}')
                ax.axvline(median_val, color='orange', linestyle='--', label=f'Median: {median_val:.2f}')
                ax.set_title(f'Histogram + KDE\nSkew: {skew_val:.2f} | Zeros: {zero_pct:.1f}%')
                ax.legend(fontsize=9)
                ax.grid(alpha=0.3)
                ax_idx += 1
            
            if 3 in selected_plots:
                ax = axes[ax_idx]
                sns.boxplot(y=df[col], ax=ax, color='lightblue')
                sns.swarmplot(y=df[col], ax=ax, color='black', alpha=0.5, size=3)
                ax.set_title('Boxplot + Swarmplot')
                ax_idx += 1
            
            if 4 in selected_plots:
                ax = axes[ax_idx]
                sns.violinplot(y=df[col], ax=ax, inner='quartile', color='lightgreen')
                ax.set_title('Violin Plot')
                ax_idx += 1
            
            if 5 in selected_plots:
                ax = axes[ax_idx]
                stats.probplot(df[col], dist="norm", plot=ax)
                ax.set_title('QQ Plot (vs Normal)')
                ax.grid(alpha=0.3)
                ax_idx += 1
            
            # Hide unused axes
            for j in range(ax_idx, len(axes)):
                axes[j].set_visible(False)
            
            plt.suptitle(f'Univariate Analysis: {col}', fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            
            figures_to_save.append((col, fig))
            
            if mode == '2':
                filename = f"{col.replace(' ', '_')}_univariate.png"
                path = os.path.join(folder, filename)
                fig.savefig(path, dpi=300, bbox_inches='tight')
                print(f"  Saved: {filename}")
                plt.close(fig)
            
            elif mode == '3':
                plt.show()
                save_this = input(f"Save plot for '{col}'? (y/n, Enter=y): ").strip().lower()
                if save_this != 'n':
                    custom_name = input(f"Filename (Enter = {col}_univariate.png): ").strip()
                    filename = custom_name if custom_name else f"{col.replace(' ', '_')}_univariate.png"
                    if not filename.endswith('.png'):
                        filename += '.png'
                    path = os.path.join(folder, filename)
                    fig.savefig(path, dpi=300, bbox_inches='tight')
                    print(f"  Saved: {path}")
                plt.close(fig)
            
            else:  # mode == '1'
                plt.show()
                plt.close(fig)
        
        if mode == '1' and figures_to_save:
            print("\n" + "="*50)
            print("All plots have been viewed.")
            save_all = input("Do you want to save ALL plots now? (y/n): ").strip().lower()
            if save_all == 'y':
                for col, fig in figures_to_save:
                    filename = f"{col.replace(' ', '_')}_univariate.png"
                    path = os.path.join(folder, filename)
                    fig.savefig(path, dpi=300, bbox_inches='tight')
                    print(f"Saved: {filename}")
                print(f"\nAll plots saved to: {os.path.abspath(folder)}")
        
        print("\nUnivariate analysis completed successfully!")
        
    except ImportError as e:
        print(f"Required library missing: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# ==========================================
# 7. BIVARIATE ANALYSIS
# ==========================================
def bivariate_analysis(df, df_info, log_list=None):
    """
    Bivariate Analysis with smart flow
    """
    print("\n" + "="*60)
    print("BIVARIATE ANALYSIS")
    print("="*60)
    
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) < 2:
        print("Not enough numeric columns for bivariate analysis.")
        return
    
    # === Correlation Options ===
    print("\nCorrelation types:")
    print("1: Pearson (linear correlation)")
    print("2: Spearman (rank correlation, good for non-linear/monotonic)")
    corr_type = input("Choose (1/2): ").strip() or '1'
    corr_method = 'pearson' if corr_type == '1' else 'spearman'
    
    # === Pairplot Options ===
    pairplot_hue = None
    if df.select_dtypes(include=['object', 'category']).shape[1] > 0:
        print("\nCategorical columns available for hue in pairplot:")
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        for i, col in enumerate(cat_cols, 1):
            print(f"{i}: {col}")
        
        use_hue = input("\nUse a column as hue in pairplot? (y/n): ").strip().lower()
        if use_hue == 'y':
            try:
                idx = int(input("Enter number (1-{}): ".format(len(cat_cols))).strip())
                pairplot_hue = cat_cols[idx - 1]
                print(f"Using '{pairplot_hue}' as hue.")
            except:
                print("Invalid selection. No hue will be used.")
    
    # === Figure Size ===
    print("\nChoose figure size:")
    print("1: Small (12x10)   2: Medium (16x14)   3: Large (20x18)   4: Custom")
    size_choice = input("Choice (1-4): ").strip() or '2'
    if size_choice == '1':
        w, h = 12, 10
    elif size_choice == '3':
        w, h = 20, 18
    elif size_choice == '4':
        custom = input("width,height: ").strip()
        try:
            w, h = map(float, custom.split(','))
        except:
            w, h = 16, 14
    else:
        w, h = 16, 14
    
    # === Save Folder ===
    folder = input("\nSave folder (Enter = current directory): ").strip() or "."
    import os
    os.makedirs(folder, exist_ok=True)
    print(f"All plots will be saved to: {os.path.abspath(folder)}")
    
    # === Viewing & Saving Mode ===
    print("\n" + "="*50)
    print("VIEWING & SAVING MODE")
    print("="*50)
    print("1: View all plots → save ALL at the end")
    print("2: Directly save all plots (no viewing)")
    print("3: View each plot → decide save individually")
    mode_input = input("Choose mode (1/2/3): ").strip() or '1'
    mode = mode_input if mode_input in ['1', '2', '3'] else '1'
    
    figures_to_save = []  # (plot_name, fig)
    
    # LOGGING FOR NOTEBOOK
    if log_list is not None:
        nb_code = [
            "numeric_cols = df.select_dtypes(include=np.number).columns",
            "# Correlation Heatmap",
            f"plt.figure(figsize=({w}, {h}))",
            f"sns.heatmap(df[numeric_cols].corr(method='{corr_method}'), annot=True, cmap='coolwarm', fmt='.2f')",
            "plt.title('Correlation Matrix')",
            "plt.show()",
            "",
            "# Pairplot",
            f"sns.pairplot(df[numeric_cols], hue='{pairplot_hue}' if '{pairplot_hue}' != 'None' else None)",
            "plt.show()"
        ]
        log_list.append(("Bivariate Analysis", nb_code))
    
    # === 1. Correlation Heatmap ===
    print("\nGenerating Correlation Heatmap...")
    corr = df[numeric_cols].corr(method=corr_method)
    
    fig_heatmap, ax_heatmap = plt.subplots(figsize=(w, h))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', vmin=-1, vmax=1,
                linewidths=0.5, linecolor='white', ax=ax_heatmap)
    ax_heatmap.set_title(f'Correlation Heatmap ({corr_method.capitalize()})', fontsize=16)
    plt.tight_layout()
    
    figures_to_save.append(('correlation_heatmap', fig_heatmap))
    
    if mode == '2':
        path = os.path.join(folder, 'correlation_heatmap.png')
        fig_heatmap.savefig(path, dpi=300, bbox_inches='tight')
        print(f"  Saved: correlation_heatmap.png")
        plt.close(fig_heatmap)
    elif mode == '3':
        plt.show()
        save = input("Save heatmap? (y/n, Enter=y): ").strip().lower()
        if save != 'n':
            path = os.path.join(folder, 'correlation_heatmap.png')
            fig_heatmap.savefig(path, dpi=300, bbox_inches='tight')
            print(f"  Saved: correlation_heatmap.png")
        plt.close(fig_heatmap)
    else:  # mode 1
        plt.show()
        plt.close(fig_heatmap)
    
    # === 2. Pairplot ===
    print("\nGenerating Pairplot...")
    try:
        pairplot_fig = sns.pairplot(df[numeric_cols], diag_kind='kde', 
                                    plot_kws={'alpha': 0.6}, hue=pairplot_hue)
        pairplot_fig.fig.suptitle('Pairplot of Numeric Features', y=1.02, fontsize=16)
        
        figures_to_save.append(('pairplot', pairplot_fig.fig))
        
        if mode == '2':
            path = os.path.join(folder, 'pairplot.png')
            pairplot_fig.fig.savefig(path, dpi=300, bbox_inches='tight')
            print(f"  Saved: pairplot.png")
            plt.close(pairplot_fig.fig)
        elif mode == '3':
            plt.show()
            save = input("Save pairplot? (y/n, Enter=y): ").strip().lower()
            if save != 'n':
                path = os.path.join(folder, 'pairplot.png')
                pairplot_fig.fig.savefig(path, dpi=300, bbox_inches='tight')
                print(f"  Saved: pairplot.png")
            plt.close(pairplot_fig.fig)
        else:  # mode 1
            plt.show()
            plt.close(pairplot_fig.fig)
    except Exception as e:
        print(f"Could not generate pairplot: {e}")
    
    # === Mode 1: Save All at End ===
    if mode == '1' and figures_to_save:
        print("\nAll plots have been viewed.")
        save_all = input("Do you want to save ALL plots now? (y/n): ").strip().lower()
        if save_all == 'y':
            for name, fig in figures_to_save:
                filename = f"{name}.png"
                path = os.path.join(folder, filename)
                fig.savefig(path, dpi=300, bbox_inches='tight')
                print(f"Saved: {filename}")
            print(f"\nAll plots saved to: {os.path.abspath(folder)}")
    
    print("\nBivariate analysis completed successfully!")

# ==========================================
# 8. MULTICOLLINEARITY
# ==========================================
def parse_correlation_plan(user_input):
    """
    Parses user input for correlation handling.
    Format: drop -1,2,3 ; keep -4,5 ;
    """
    plan = {'drop': set(), 'keep': set()}
    
    if not user_input.strip():
        return plan
    
    parts = [p.strip() for p in user_input.split(';') if p.strip()]
    
    for part in parts:
        action = None
        if part.startswith('drop'):
            action = 'drop'
        elif part.startswith('keep'):
            action = 'keep'
        else:
            print(f"Warning: Unknown action in '{part}'. Skipping.")
            continue
        
        if '-' not in part:
            print(f"Warning: No IDs found in '{part}'. Skipping.")
            continue
        
        id_part = part.split('-', 1)[1].strip()
        ids = set()
        
        for sub in [s.strip() for s in id_part.split(',')]:
            if '-' in sub:
                try:
                    start, end = map(int, sub.split('-'))
                    ids.update(range(start, end + 1))
                except:
                    print(f"Invalid range '{sub}'. Skipping.")
            else:
                try:
                    ids.add(int(sub))
                except:
                    print(f"Invalid ID '{sub}'. Skipping.")
        
        plan[action].update(ids)
    
    return plan

def handle_high_correlation(df, df_info, log_list=None, threshold=0.90):
    """
    Detects highly correlated features and suggests dropping redundant ones.
    """
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_cols) < 2:
        print("Not enough numeric columns to check for correlation.")
        return df, df_info

    print(f"\n=== HIGH CORRELATION CHECK (Threshold > {threshold}) ===")
    
    # Calculate Correlation Matrix
    corr_matrix = df[numeric_cols].corr().abs()
    
    # Select upper triangle of correlation matrix
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    
    # Find columns with correlation greater than threshold
    high_corr_data = []
    high_corr_cols = set()
    
    for col in upper.columns:
        high_corr_series = upper[col][upper[col] > threshold]
        if not high_corr_series.empty:
            high_corr_cols.add(col)
            for match_col, val in high_corr_series.items():
                high_corr_data.append({
                    'column_name': col,
                    'correlated_with': match_col,
                    'val': val
                })
    
    if not high_corr_cols:
        print("No columns found with correlation above the threshold. Good to go!")
        return df, df_info

    # Map to IDs for display
    corr_summary = pd.DataFrame(high_corr_data)
    
    print(f"\nDetected {len(high_corr_cols)} columns that are highly correlated with others:\n")
    
    cols_with_issues = df_info[df_info['column_name'].isin(high_corr_cols)].copy()
    
    for idx, row in cols_with_issues.iterrows():
        c_name = row['column_name']
        c_id = row['id']
        conflicts = corr_summary[corr_summary['column_name'] == c_name]
        conflict_str = ", ".join([f"{r['correlated_with']} ({r['val']:.2f})" for _, r in conflicts.iterrows()])
        print(f"ID {c_id} | {c_name} <--> {conflict_str}")

    # === GLOBAL SUGGESTION ===
    global_suggestion = {row['id']: 'drop' for _, row in cols_with_issues.iterrows()}
    
    print("\n=== GLOBAL SUGGESTION FOR CORRELATION ===")
    for col_id, action in global_suggestion.items():
        col_name = df_info[df_info['id'] == col_id]['column_name'].iloc[0]
        print(f"ID {col_id} ({col_name}): {action}")

    approve = input("\nDo you approve this global suggestion? (y/n): ").strip().lower()
    
    updated_df = df.copy()
    updated_info = df_info.copy()
    
    if approve == 'y':
        user_plan = {'drop': set(global_suggestion.keys()), 'keep': set()}
    else:
        print("\nProvide your custom plan in this format:")
        print("drop -1,2 ; keep -3,4 ;")
        print("(Note: 'keep' means you accept the high correlation and do nothing)")
        user_input = input("Your plan: ").strip()
        user_plan = parse_correlation_plan(user_input)

    # === Covered / Uncovered ===
    covered_ids = set()
    for ids in user_plan.values():
        covered_ids.update(ids)
    
    all_issue_ids = set(cols_with_issues['id'])
    uncovered_ids = all_issue_ids - covered_ids
    
    # Logging Container
    log_code = []

    # Apply user's plan
    ids_to_drop = [cid for cid in user_plan['drop'] if cid in all_issue_ids]
    
    for col_id in ids_to_drop:
        col_name = updated_info[updated_info['id'] == col_id]['column_name'].iloc[0]
        print(f"Dropping correlated column: {col_name}")
        updated_df.drop(columns=[col_name], inplace=True)
        updated_info = updated_info[updated_info['id'] != col_id]
        # Log
        log_code.append(f"df.drop(columns=['{col_name}'], inplace=True)")

    ids_to_keep = [cid for cid in user_plan['keep'] if cid in all_issue_ids]
    for col_id in ids_to_keep:
        col_name = df_info[df_info['id'] == col_id]['column_name'].iloc[0]
        print(f"Keeping correlated column: {col_name}")

    # === Handle Uncovered Columns ===
    if uncovered_ids:
        print(f"\n⚠️  The following correlated columns were NOT mentioned:")
        print(cols_with_issues[cols_with_issues['id'].isin(uncovered_ids)][['id', 'column_name']])
        
        while True:
            choice = input("\nWhat to do with these columns?\n"
                           "1: Provide custom actions now\n"
                           "2: Apply original suggestion (Drop all)\n"
                           "3: Keep all (Do nothing)\n"
                           "Enter 1, 2, or 3: ").strip()
            
            if choice == '1':
                extra_input = input("Additional plan (drop -X; keep -Y): ").strip()
                extra_plan = parse_correlation_plan(extra_input)
                
                # Process Drops
                extra_drops = [cid for cid in extra_plan['drop'] if cid in uncovered_ids]
                for col_id in extra_drops:
                    col_name = df_info[df_info['id'] == col_id]['column_name'].iloc[0]
                    if col_name in updated_df.columns:
                        print(f"Dropping: {col_name}")
                        updated_df.drop(columns=[col_name], inplace=True)
                        updated_info = updated_info[updated_info['id'] != col_id]
                        log_code.append(f"df.drop(columns=['{col_name}'], inplace=True)")
                
                # Process Keeps
                extra_keeps = [cid for cid in extra_plan['keep'] if cid in uncovered_ids]
                for col_id in extra_keeps:
                    col_name = df_info[df_info['id'] == col_id]['column_name'].iloc[0]
                    print(f"Keeping: {col_name}")
                break
                
            elif choice == '2':
                print("Dropping remaining highly correlated columns...")
                for col_id in uncovered_ids:
                    col_name = df_info[df_info['id'] == col_id]['column_name'].iloc[0]
                    if col_name in updated_df.columns:
                        print(f"Dropping: {col_name}")
                        updated_df.drop(columns=[col_name], inplace=True)
                        updated_info = updated_info[updated_info['id'] != col_id]
                        log_code.append(f"df.drop(columns=['{col_name}'], inplace=True)")
                break
                
            elif choice == '3':
                print("Keeping remaining columns.")
                break
            else:
                print("Invalid choice.")
    
    # Re-index IDs after drops
    updated_info.reset_index(drop=True, inplace=True)
    updated_info['id'] = range(1, len(updated_info) + 1)
    
    print(f"\nCorrelation handling complete. Final shape: {updated_df.shape}")
    
    # Logging
    if log_list is not None and log_code:
        log_list.append(("Handle Multicollinearity", log_code))
        
    return updated_df, updated_info

# ==========================================
# 9. ENCODING
# ==========================================
def handle_categorical_encoding(df, df_info, log_list=None):
    """
    1. Identifies object/categorical columns.
    2. Suggests one_hot or label based on cardinality.
    """
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(cat_cols) == 0:
        print("No categorical columns found. Skipping encoding.")
        return df, df_info

    print("\n=== CATEGORICAL ENCODING ===")
    print("Converting text columns to numbers for ML models.\n")
    
    # Analyze cardinality
    cat_data = []
    for col in cat_cols:
        unique_count = df[col].nunique()
        cat_data.append({'column_name': col, 'unique_count': unique_count})
        
    cat_summary = pd.DataFrame(cat_data)
    
    # Map to IDs
    cat_info = df_info[df_info['column_name'].isin(cat_cols)].copy()
    cat_info = cat_info.merge(cat_summary, on='column_name')
    
    print(cat_info[['id', 'column_name', 'unique_count']].to_string(index=False))
    
    # Generate Suggestions
    global_suggestion = {}
    for _, row in cat_info.iterrows():
        col_id = row['id']
        if row['unique_count'] <= 10:
            global_suggestion[col_id] = 'one_hot'
        else:
            global_suggestion[col_id] = 'label'

    print("\n=== GLOBAL SUGGESTION ===")
    for col_id, action in global_suggestion.items():
        col_name = df_info[df_info['id'] == col_id]['column_name'].iloc[0]
        u_count = cat_info[cat_info['id'] == col_id]['unique_count'].iloc[0]
        print(f"ID {col_id} ({col_name}): {action} (Unique: {u_count})")

    approve = input("\nDo you approve? (y/n): ").strip().lower()
    
    if approve == 'y':
        user_plan = {'one_hot': set(), 'label': set(), 'skip': set()}
        for cid, act in global_suggestion.items():
            user_plan[act].add(cid)
    else:
        print("\nFormat: one_hot -1,2 ; label -3 ; skip -4 ;")
        user_input = input("Your plan: ").strip()
        
        user_plan = {'one_hot': set(), 'label': set(), 'skip': set()}
        parts = [p.strip() for p in user_input.split(';') if p.strip()]
        for part in parts:
            if 'one_hot' in part: key = 'one_hot'
            elif 'label' in part: key = 'label'
            elif 'skip' in part: key = 'skip'
            else: continue
            
            try:
                id_str = part.split('-')[1]
                ids = set()
                for x in id_str.split(','):
                    if '-' in x:
                        s, e = map(int, x.split('-'))
                        ids.update(range(s, e+1))
                    else:
                        ids.add(int(x))
                user_plan[key].update(ids)
            except:
                print(f"Error parsing '{part}'")

    # Apply Logic
    updated_df = df.copy()
    log_code = []

    # Process Label Encoding first
    le_ids = [cid for cid in user_plan['label'] if cid in cat_info['id'].values]
    for col_id in le_ids:
        col_name = df_info[df_info['id'] == col_id]['column_name'].iloc[0]
        le = LabelEncoder()
        updated_df[col_name] = le.fit_transform(updated_df[col_name].astype(str))
        print(f"Label Encoded: {col_name}")
        log_code.append(f"le = LabelEncoder()")
        log_code.append(f"df['{col_name}'] = le.fit_transform(df['{col_name}'].astype(str))")

    # Process One-Hot
    oh_ids = [cid for cid in user_plan['one_hot'] if cid in cat_info['id'].values]
    cols_to_dummy = [df_info[df_info['id'] == cid]['column_name'].iloc[0] for cid in oh_ids]
    
    if cols_to_dummy:
        print(f"One-Hot Encoding: {cols_to_dummy}")
        updated_df = pd.get_dummies(updated_df, columns=cols_to_dummy, drop_first=True)
        log_code.append(f"df = pd.get_dummies(df, columns={cols_to_dummy}, drop_first=True)")
    
    # Logging
    if log_list is not None and log_code:
        log_list.append(("Categorical Encoding", log_code))

    new_info = get_df_info(updated_df)
    return updated_df, new_info

# ==========================================
# 10. SCALING
# ==========================================
def handle_feature_scaling(df, df_info, log_list=None):
    """
    1. Identifies numeric columns.
    2. Suggests: 'standard' or 'minmax' based on skew.
    """
    numeric_cols = df.select_dtypes(include=['float64', 'int64', 'int32']).columns
    
    # Filter out binary columns (0/1) created by one-hot encoding, usually don't need scaling
    numeric_cols = [c for c in numeric_cols if df[c].nunique() > 2]
    
    if not numeric_cols:
        print("No numeric columns require scaling.")
        return df, df_info

    print("\n=== FEATURE SCALING ===")
    print("Normalizing the range of independent variables.\n")
    
    scaling_data = []
    for col in numeric_cols:
        skew = df[col].skew()
        scaling_data.append({'column_name': col, 'skew': skew})
        
    scale_summary = pd.DataFrame(scaling_data)
    scale_info = df_info[df_info['column_name'].isin(numeric_cols)].copy()
    scale_info = scale_info.merge(scale_summary, on='column_name')

    print(scale_info[['id', 'column_name', 'skew']].to_string(index=False))

    # Global Suggestion
    global_suggestion = {}
    for _, row in scale_info.iterrows():
        col_id = row['id']
        if abs(row['skew']) < 1:
            global_suggestion[col_id] = 'standard'
        else:
            global_suggestion[col_id] = 'minmax'
            
    print("\n=== GLOBAL SUGGESTION ===")
    for col_id, action in global_suggestion.items():
        col_name = df_info[df_info['id'] == col_id]['column_name'].iloc[0]
        skew = scale_info[scale_info['id'] == col_id]['skew'].iloc[0]
        print(f"ID {col_id} ({col_name}): {action} (Skew: {skew:.2f})")

    approve = input("\nDo you approve? (y/n): ").strip().lower()
    
    user_plan = {'standard': set(), 'minmax': set(), 'skip': set()}
    if approve == 'y':
        for cid, act in global_suggestion.items():
            user_plan[act].add(cid)
    else:
        print("\nFormat: standard -1,2 ; minmax -3 ; skip -4 ;")
        user_input = input("Your plan: ").strip()
        
        parts = [p.strip() for p in user_input.split(';') if p.strip()]
        for part in parts:
            if 'standard' in part: key = 'standard'
            elif 'minmax' in part: key = 'minmax'
            elif 'skip' in part: key = 'skip'
            else: continue
            try:
                id_str = part.split('-')[1]
                ids = set()
                for x in id_str.split(','):
                    if '-' in x:
                        s, e = map(int, x.split('-'))
                        ids.update(range(s, e+1))
                    else:
                        ids.add(int(x))
                user_plan[key].update(ids)
            except: pass

    updated_df = df.copy()
    log_code = []
    
    # Apply Standard Scaler
    std_ids = [cid for cid in user_plan['standard'] if cid in scale_info['id'].values]
    if std_ids:
        std_cols = [df_info[df_info['id'] == cid]['column_name'].iloc[0] for cid in std_ids]
        scaler = StandardScaler()
        updated_df[std_cols] = scaler.fit_transform(updated_df[std_cols])
        print(f"StandardScaled: {len(std_cols)} columns")
        log_code.append(f"scaler = StandardScaler()")
        log_code.append(f"df[{std_cols}] = scaler.fit_transform(df[{std_cols}])")
        
    # Apply MinMax Scaler
    mm_ids = [cid for cid in user_plan['minmax'] if cid in scale_info['id'].values]
    if mm_ids:
        mm_cols = [df_info[df_info['id'] == cid]['column_name'].iloc[0] for cid in mm_ids]
        scaler = MinMaxScaler()
        updated_df[mm_cols] = scaler.fit_transform(updated_df[mm_cols])
        print(f"MinMaxScaled: {len(mm_cols)} columns")
        log_code.append(f"scaler = MinMaxScaler()")
        log_code.append(f"df[{mm_cols}] = scaler.fit_transform(df[{mm_cols}])")

    # Logging
    if log_list is not None and log_code:
        log_list.append(("Feature Scaling", log_code))

    return updated_df, df_info

# ==========================================
# 11. MAIN EXECUTION FLOW
# ==========================================
if __name__ == "__main__":
    # Initialize Log List
    notebook_log = []
    
    df = load_csv_to_dataframe(notebook_log)
    if df is not None:
        info = get_df_info(df)
        print("\nInitial column info:")
        print(info)
        
        # Drop Columns
        df = drop_columns_by_id(df, info, notebook_log)
        if df.shape[1] != info.shape[0]:
            info = get_df_info(df)
            print("\nUpdated column info after dropping columns:")
            print(info)
        
        # Missing Values
        df, info = handle_missing_values(df, info, notebook_log)
        
        print("\nFinal column info after missing value handling:")
        print(info)
        
        # Outliers
        df, info = detect_and_handle_outliers(df, info, notebook_log)
        
        print("\nFinal column info after outlier handling:")
        print(info)
        
        # Univariate
        do_univariate = input("\nDo you want to perform univariate analysis (stats + optional plots)? (y/n): ").strip().lower()
        if do_univariate == 'y':
            univariate_analysis(df, info, notebook_log)
            
        # Bivariate
        do_bivariate = input("\nDo you want to perform bivariate analysis (correlation heatmap + pairplot)? (y/n): ").strip().lower()
        if do_bivariate == 'y':
            bivariate_analysis(df, info, notebook_log)
            
            # Correlation Drop (Nested under Bivariate usually)
            do_drop_corr = input("\nDo you want to drop highly correlated columns based on the analysis? (y/n): ").strip().lower()
            if do_drop_corr == 'y':
                thresh_input = input("Enter correlation threshold (default 0.90): ").strip()
                try:
                    threshold = float(thresh_input)
                except:
                    threshold = 0.90
                
                df, info = handle_high_correlation(df, info, notebook_log, threshold)
        
        # Encoding
        do_encode = input("\nDo you want to encode categorical columns (One-Hot/Label)? (y/n): ").strip().lower()
        if do_encode == 'y':
            df, info = handle_categorical_encoding(df, info, notebook_log)
            print("\nUpdated column info after encoding:")
            print(info)

        # Scaling
        do_scale = input("\nDo you want to scale numeric features (Standard/MinMax)? (y/n): ").strip().lower()
        if do_scale == 'y':
            df, info = handle_feature_scaling(df, info, notebook_log)

        print("\n=== FINAL CLEAN DATASET READY ===")
        print(f"Shape: {df.shape}")
        print(info)
        
        # === GENERATE NOTEBOOK ===
        print("\n" + "="*50)
        print("WORKFLOW COMPLETE")
        print("="*50)
        gen_nb = input("Do you want to download the Python Code (.ipynb) for this workflow? (y/n): ").strip().lower()
        if gen_nb == 'y':
            fname = input("Enter filename for notebook (default: workflow.ipynb): ").strip()
            if not fname: fname = "workflow.ipynb"
            save_to_ipynb(notebook_log, filename=fname)
        
        # Optional: Save clean data
        save = input("\nSave cleaned dataset to CSV? (y/n): ").strip().lower()
        if save == 'y':
            filename = input("Enter filename (e.g., clean_weather.csv): ").strip()
            if not filename.endswith('.csv'):
                filename += '.csv'
            df.to_csv(filename, index=False)
            print(f"Saved to {filename}")