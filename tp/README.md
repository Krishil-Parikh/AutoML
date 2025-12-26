# AutoML FastAPI Backend

This project exposes your Auto EDA workflow as a web API using FastAPI. It mirrors the logic in `auto-eda-2.py` (load → drop columns → handle missing values → outliers → correlation → encoding → scaling → analysis → export).

## Quick Start

1) Install dependencies

```bash
pip install -r requirements.txt
```

2) Ensure MongoDB is running locally (used for logging steps and notebook generation). Default URI in code: `mongodb://localhost:27017/`.

3) Run the API

```bash
uvicorn backend:app --reload --port 8000
```

Open docs at: http://localhost:8000/docs

## API Flow

- Upload CSV: `POST /upload` (multipart file)
- Inspect dataset info: `GET /info/{session_id}`
- Drop columns: `POST /clean/drop` with `{ session_id, column_ids }`
- Missing value suggestions: `GET /suggestions/missing/{session_id}`
- Apply missing plan: `POST /clean/missing` with `{ session_id, plan }`
- Outlier suggestions: `GET /suggestions/outliers/{session_id}`
- Apply outlier plan: `POST /clean/outliers` with `{ session_id, plan }`
- Handle correlation: `POST /clean/correlation` (auto or manual drop)
- Encoding suggestions: `GET /suggestions/encoding/{session_id}`
- Apply encoding: `POST /clean/encoding` with `{ session_id, plan }`
- Scaling suggestions: `GET /suggestions/scaling/{session_id}`
- Apply scaling: `POST /clean/scaling` with `{ session_id, plan }`
- Univariate stats: `GET /analysis/univariate/{session_id}`
- Bivariate corr: `GET /analysis/bivariate/{session_id}`
- Download notebook: `POST /download/notebook` with `{ session_id, filename }`
- Download cleaned CSV: `GET /download/csv/{session_id}`

## Example Requests

Upload CSV:

```bash
curl -F "file=@path/to/your.csv" http://localhost:8000/upload
```

Drop columns (by IDs from `/info`):

```bash
curl -X POST http://localhost:8000/clean/drop \
	-H "Content-Type: application/json" \
	-d '{"session_id":"<SESSION>","column_ids":[1,3,5]}'
```

Apply missing plan (example):

```bash
curl -X POST http://localhost:8000/clean/missing \
	-H "Content-Type: application/json" \
	-d '{
		"session_id":"<SESSION>",
		"plan": {"mean": [2], "median": [4], "mode": [7], "drop_col": [9]}
	}'
```

Auto-drop high correlation (threshold 0.90 default):

```bash
curl -X POST http://localhost:8000/clean/correlation \
	-H "Content-Type: application/json" \
	-d '{"session_id":"<SESSION>", "auto_drop": true, "threshold": 0.9}'
```

Download notebook:

```bash
curl -X POST http://localhost:8000/download/notebook \
	-H "Content-Type: application/json" \
	-d '{"session_id":"<SESSION>", "filename": "workflow"}' --output workflow.ipynb
```

Download cleaned CSV:

```bash
curl -L http://localhost:8000/download/csv/<SESSION> --output clean_data.csv
```

## Notes

- The backend stores session data as Parquet (`pyarrow` required) and logs steps to MongoDB for notebook generation.
- If you don’t want MongoDB, we can add an in-memory or file-based fallback on request.