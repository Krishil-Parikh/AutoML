# Backend Architecture

The backend has been refactored into a clean, modular structure for better maintainability and scalability.

## File Organization

### Core Application
- **`backend.py`** (715 lines) - Main FastAPI application with all API endpoints
  - Health checks & session management
  - Column management endpoints
  - Missing values handling endpoints
  - Outlier detection endpoints
  - Correlation analysis endpoints
  - Encoding endpoints
  - Scaling endpoints
  - Analysis endpoints (univariate, bivariate)
  - Plot generation endpoints
  - Download endpoints

### Pydantic Models
- **`schemas.py`** - Request/Response Pydantic models
  - `DropColumnsModel`
  - `MissingValuesPlan`
  - `OutlierPlan`
  - `CorrelationPlan`
  - `EncodingPlan`
  - `ScalingPlan`

### Data Processing Modules
- **`data_utils.py`** - Data loading and information utilities
  - `load_csv_to_dataframe()`
  - `get_df_info()`

- **`column_ops.py`** - Column management functions
  - `drop_columns_by_id()`

- **`missing_values.py`** - Missing value handling
  - `handle_missing_values()`
  - `generate_global_suggestion()`
  - `parse_user_plan()`

- **`outliers.py`** - Outlier detection and handling
  - `detect_and_handle_outliers()`
  - `parse_outlier_plan()`

- **`correlation_utils.py`** - Correlation and multicollinearity handling
  - `handle_high_correlation()`
  - `parse_correlation_plan()`

- **`encoding_utils.py`** - Categorical encoding
  - `handle_categorical_encoding()`

- **`scaling_utils.py`** - Feature scaling
  - `handle_feature_scaling()`

### Analysis Modules
- **`analysis.py`** - Data analysis functions
  - `univariate_analysis()`
  - `bivariate_analysis()`

### Utility Modules
- **`notebook_utils.py`** - Jupyter notebook generation
  - `save_to_ipynb()`
  - `notebook_bytes()`

- **`storage.py`** - Session and storage management
  - `_session_path()`
  - `_load_df()`
  - `_save_df()`
  - `_log()`
  - `_SESSION_LOGS` (global dict)

- **`scheduler_utils.py`** - Scheduler configuration
- **`config.py`** - Configuration management

## Refactoring Benefits

✅ **Separation of Concerns** - Each module has a single responsibility
✅ **Improved Maintainability** - Easy to locate and modify specific functionality
✅ **Better Testing** - Each module can be tested independently
✅ **Reduced File Size** - Main backend.py reduced from 2196 lines to 715 lines
✅ **Reusability** - Functions can be imported and used in other applications
✅ **Clear Dependencies** - Explicit imports show what each module needs

## API Endpoints Organization

### Health & Session (3 endpoints)
```
GET  /              - Root endpoint
GET  /health        - Health check
POST /upload        - Upload CSV file
GET  /info/{id}     - Get session info
```

### Column Management (1 endpoint)
```
POST /clean/drop    - Drop columns
```

### Missing Values (2 endpoints)
```
GET  /suggestions/missing/{id}     - Get suggestions
POST /clean/missing                - Apply handling
```

### Outliers (2 endpoints)
```
GET  /suggestions/outliers/{id}    - Get suggestions
POST /clean/outliers               - Apply handling
```

### Correlation (1 endpoint)
```
POST /clean/correlation            - Handle multicollinearity
```

### Encoding (2 endpoints)
```
GET  /suggestions/encoding/{id}    - Get suggestions
POST /clean/encoding               - Apply encoding
```

### Scaling (2 endpoints)
```
GET  /suggestions/scaling/{id}     - Get suggestions
POST /clean/scaling                - Apply scaling
```

### Analysis (2 endpoints)
```
GET  /analysis/univariate/{id}     - Univariate stats
GET  /analysis/bivariate/{id}      - Bivariate stats
```

### Plots (4 endpoints)
```
GET  /plots/univariate/{id}/{col}          - Single column plot
GET  /plots/univariate/{id}                - All columns plots (ZIP)
GET  /plots/bivariate/heatmap/{id}         - Correlation heatmap
GET  /plots/bivariate/pairplot/{id}        - Pairplot
```

### Downloads (2 endpoints)
```
POST /download/notebook            - Download as .ipynb
GET  /download/csv/{id}            - Download as CSV
```

## Code Statistics

- **Before**: 2196 lines in single backend.py
- **After**: 715 lines in backend.py + organized modules
- **Reduction**: 67% smaller main file
- **Better Organization**: 12+ specialized modules

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the backend
python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
```

## Module Dependencies

```
backend.py
├── notebook_utils.py
├── data_utils.py
├── missing_values.py
├── outliers.py
├── analysis.py
├── correlation_utils.py
├── encoding_utils.py
├── scaling_utils.py
├── column_ops.py
├── storage.py
└── schemas.py
```

## Notes

- All functions maintain the same API and behavior
- No business logic has been changed
- Clean modular structure with proper documentation
- Easy to extend and maintain
