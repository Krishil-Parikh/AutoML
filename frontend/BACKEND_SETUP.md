# Backend Setup Guide

## Quick Start

Your FastAPI backend should contain the Python code you provided. Here's how to set it up:

### 1. Create Backend Directory

```bash
mkdir backend
cd backend
```

### 2. Save Your Python Code

Save your FastAPI backend code as `main.py` in the backend directory.

### 3. Install Dependencies

```bash
pip install fastapi uvicorn pandas numpy scikit-learn matplotlib seaborn scipy python-multipart
```

Or create a `requirements.txt`:

```txt
fastapi==0.104.1
uvicorn==0.24.0
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
matplotlib==3.8.2
seaborn==0.13.0
scipy==1.11.4
python-multipart==0.0.6
```

Then install:

```bash
pip install -r requirements.txt
```

### 4. Run the Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### 5. Verify Backend is Running

Open your browser and go to:
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/`

### 6. Start the Frontend

In a new terminal, from the project root:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

The backend provides these endpoints:

- `POST /upload` - Upload CSV file
- `GET /info/{session_id}` - Get column information
- `POST /clean/drop` - Drop selected columns
- `GET /suggestions/missing/{session_id}` - Get missing value suggestions
- `POST /clean/missing` - Apply missing value plan
- `GET /suggestions/outliers/{session_id}` - Get outlier suggestions
- `POST /clean/outliers` - Apply outlier plan
- `POST /clean/correlation` - Handle correlation
- `GET /suggestions/encoding/{session_id}` - Get encoding suggestions
- `POST /clean/encoding` - Apply encoding plan
- `GET /suggestions/scaling/{session_id}` - Get scaling suggestions
- `POST /clean/scaling` - Apply scaling plan
- `GET /plots/bivariate/heatmap/{session_id}` - Generate correlation heatmap
- `GET /download/csv/{session_id}` - Download cleaned CSV
- `POST /download/notebook` - Download Jupyter Notebook

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console, add this to your FastAPI backend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Port Already in Use

If port 8000 is in use, change it in:
1. Backend: `uvicorn main:app --reload --port 8001`
2. Frontend: Update `.env` file: `VITE_API_URL=http://localhost:8001`

### Module Not Found

Make sure all dependencies are installed:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```
