from pydantic import BaseModel

"""
config_path:
metric_path:
test_path:
output_path:
"""


class TrainingSchema(BaseModel):
    config_path: str
    metric_path: str
    test_path: str
    output_path: str
