from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Patient:
    age: int
    sex: str  # "MALE", "FEMALE", "ALL"
    diagnosis: str
    stage: Optional[str] = None
    prior_chemo: bool = False
    months_since_last_treatment: Optional[int] = None
    ecog_status: Optional[int] = None  # 0-5 performance scale
    labs: dict = field(default_factory=dict)  # e.g. {"creatinine": 1.2, "anc": 1800}
    medications: List[str] = field(default_factory=list)
