from dataclasses import fields, is_dataclass
from enum import Enum
from types import NoneType
from typing import get_args, get_origin


class SerializationException(Exception):
    pass


def serialize(obj):
    if isinstance(obj, (NoneType, bool, int, float, str)):
        return obj
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, tuple):
        return [serialize(i) for i in obj]
    elif isinstance(obj, list):
        if obj and isinstance(obj[0], list):
            return [{'row': serialize(i)} for i in obj]
        return [serialize(i) for i in obj]
    elif hasattr(obj, '__dict__'):
        d = vars(obj)
        return {k: serialize(d[k]) for k in d}
    
    raise SerializationException(f'Type {type(obj)} not supported')
    
def deserialize(obj, hint: type):
    if isinstance(obj, NoneType):
        return obj
    elif hint in [bool, int, float, str]:
        return obj
    elif issubclass(hint, Enum):
        return hint(obj)
    elif get_origin(hint) == tuple:
        args = get_args(hint)
        return tuple(deserialize(o, h) for o, h in zip(obj, args))
    elif get_origin(hint) == list:
        [h] = get_args(hint)
        if get_origin(h) == list:
            return [deserialize(o['row'], h) for o in obj]
        return [deserialize(o, h) for o in obj]
    elif is_dataclass(hint):
        args = fields(hint)
        return hint(**{f.name: deserialize(obj[f.name], f.type) for f in args})
    
    raise SerializationException(f'Type {hint} not supported')
