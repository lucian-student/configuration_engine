from configuration_engine.parameter import (
    ClassCallableSchema,
    RangeParameterSchema,
    LiteralParameterSchema,
)

TunableDictSchema = dict[
    str,
    ClassCallableSchema
    | RangeParameterSchema[int]
    | RangeParameterSchema[float]
    | LiteralParameterSchema[int | float | str | bool]
    | int
    | float
    | str
    | bool,
]

NonTunableDictSchema = dict[str, int | float | str | bool]
