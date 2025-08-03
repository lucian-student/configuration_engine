from pydantic import BaseModel
from typing import Optional, Literal


class Metadata(BaseModel):
    name: str
    # pokud je output path, none tak se použije string logger
    output_path: Optional[str]
    seed: int
    tuner: Literal["grid", "optuna"] = "optuna"
    cv: bool = True
