from pydantic import BaseModel


class DropColumnsModel(BaseModel):
    session_id: str
    column_ids: list[int]


class MissingValuesPlan(BaseModel):
    session_id: str
    plan: dict[str, list[int]]


class OutlierPlan(BaseModel):
    session_id: str
    plan: dict[str, list[int]]


class CorrelationPlan(BaseModel):
    session_id: str
    threshold: float = 0.90
    plan: dict[str, list[int]] | None = None
    auto_drop: bool = False


class EncodingPlan(BaseModel):
    session_id: str
    plan: dict[str, list[int]]


class ScalingPlan(BaseModel):
    session_id: str
    plan: dict[str, list[int]]
