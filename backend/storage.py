import pandas as pd
from fastapi import HTTPException

# In-memory storage - no files written to disk
_SESSION_DATA: dict = {}  # session_id -> dataframe
_SESSION_LOGS: dict = {}  # session_id -> list of logs


def _load_df(session_id: str) -> pd.DataFrame:
    """Load dataframe from memory."""
    if session_id not in _SESSION_DATA:
        raise HTTPException(status_code=404, detail="Session not found")
    return _SESSION_DATA[session_id]


def _save_df(session_id: str, df: pd.DataFrame) -> None:
    """Save dataframe to memory."""
    _SESSION_DATA[session_id] = df.copy()


def _log(session_id: str, step: str, code_lines: list[str]) -> None:
    """Log processing steps for a session."""
    _SESSION_LOGS.setdefault(session_id, []).append((step, code_lines))


def get_logs(session_id: str):
    """Get logs for a session."""
    return _SESSION_LOGS.get(session_id, [])


def _cleanup_session(session_id: str) -> None:
    """Clean up session data from memory."""
    _SESSION_DATA.pop(session_id, None)
    _SESSION_LOGS.pop(session_id, None)
