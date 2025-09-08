# utils/deprecate.py 或 plugins/deprecate.py
import functools
import warnings


def deprecated(reason: str = ""):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"Function `{func.__name__}` is deprecated."
            if reason:
                msg += f" {reason}"
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return None

        return wrapper

    return decorator
