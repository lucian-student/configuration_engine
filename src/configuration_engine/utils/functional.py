import importlib
from types import ModuleType
from typing import Optional, Iterable
import inspect


def resolve_function(
    path: str, allowed_modules: Optional[Iterable[str]] = None, class_only: bool = True
):
    """
    Convert a string like 'math.sqrt' or 'my_module.my_func' into a callable.
    Only allows functions from explicitly whitelisted modules if provided.
    """
    parts = path.split(".")
    if len(parts) < 2:
        raise ValueError("Built-in functions are not supported. Use full module path.")

    module_path = ".".join(parts[:-1])
    func_name = parts[-1]

    if allowed_modules and module_path not in allowed_modules:
        raise ImportError(f"Module '{module_path}' is not in the allowed list.")

    module: ModuleType = importlib.import_module(module_path)

    try:
        func = getattr(module, func_name)
    except AttributeError:
        raise AttributeError(
            f"Function '{func_name}' not found in module '{module_path}'."
        )

    if not callable(func):
        raise TypeError(f"'{func_name}' in module '{module_path}' is not function.")

    if class_only and not inspect.isclass(func):
        raise ValueError("Class only flag allows only callable classes!")

    return func
