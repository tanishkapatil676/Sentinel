from pydantic import BaseModel, Field
from typing import List, Optional

class NumericSummaryInput(BaseModel):
    numbers: List[float] = Field(..., description="List of numbers to process", min_length=1, max_length=1000)

class NumericSummaryResult(BaseModel):
    count: int
    sum: float
    mean: float
    min: float
    max: float
