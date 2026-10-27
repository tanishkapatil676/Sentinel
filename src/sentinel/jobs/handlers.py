from typing import Dict, Any
from sentinel.jobs.schemas import NumericSummaryInput, NumericSummaryResult

def compute_numeric_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic job handler for bounded numeric summary computation.
    Validates input using Pydantic and returns computed statistics.
    """
    validated_input = NumericSummaryInput(**payload)
    numbers = validated_input.numbers

    count = len(numbers)
    total_sum = sum(numbers)
    mean = total_sum / count if count > 0 else 0.0
    min_val = min(numbers)
    max_val = max(numbers)

    result = NumericSummaryResult(
        count=count,
        sum=total_sum,
        mean=mean,
        min=min_val,
        max=max_val
    )
    return result.model_dump()
