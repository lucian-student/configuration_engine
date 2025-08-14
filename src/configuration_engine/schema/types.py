from configuration_engine.parameter import (
    CallableParameterSchema,
    RangeParameterSchema,
    LiteralParameterSchema,
)

TunableDictSchema = dict[
    str,
    CallableParameterSchema
    | RangeParameterSchema[int]
    | RangeParameterSchema[float]
    | LiteralParameterSchema[int | float | str | bool]
    | int
    | float
    | str
    | bool,
]

NonTunableDictSchema = dict[str, int | float | str | bool]
