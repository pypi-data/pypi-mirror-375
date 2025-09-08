from __future__ import annotations
from typing import Any, Iterable, Literal, get_type_hints
import inspect
import functools
from pydantic import BaseModel, create_model
from .registry import REGISTRY, TunableEntry
from .context import _active_trace, _active_cfg
from .naming import ns_to_field

def tunable(*include: str, namespace: str|None=None, mode: Literal["include","exclude"]="include",
            exclude: Iterable[str]|None=None, apps: Iterable[str]=()):
    """Mark a function's selected parameters as user-tunable.
    - include: names to include. If empty, include all params that have defaults
               (unless mode='exclude' with an explicit exclude list).
    - namespace: JSON section name; defaults to 'module.function'.
    - apps: optional tags to group functions per executable/app.
    """
    include_set = set(include) if include else None
    exclude_set = set(exclude or ())

    def decorator(fn):
        sig = inspect.signature(fn)
        hints = get_type_hints(fn)
        fields: dict[str, tuple[type[Any], Any]] = {}
        for name, p in sig.parameters.items():
            if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
                continue
            if include_set is not None:
                selected = name in include_set
            elif mode == "exclude" and exclude_set:
                selected = (p.default is not inspect._empty) and (name not in exclude_set)
            else:
                selected = (p.default is not inspect._empty)
            if not selected:
                continue
            ann = hints.get(name, Any)
            default = p.default if p.default is not inspect._empty else ...
            fields[name] = (ann, default)

        ns = namespace or f"{fn.__module__}.{fn.__name__}"
        model_name = f"{ns.title().replace('.','').replace('_','')}Config"
        Model = create_model(model_name, **fields)  # type: ignore

        REGISTRY.register(TunableEntry(fn=fn, model=Model, sig=sig, namespace=ns, apps=set(apps)))

        @functools.wraps(fn)
        def wrapper(*args, cfg: BaseModel | dict | None = None, **kwargs):
            tracer = _active_trace.get()
            if tracer is not None:
                tracer.namespaces.add(ns)
                if tracer.noop:
                    return None

            if cfg is not None:
                data = cfg if isinstance(cfg, dict) else cfg.model_dump()
                filtered = {k: v for k, v in data.items() if k in sig.parameters}
                return fn(*args, **filtered, **kwargs)

            app_cfg = _active_cfg.get()
            if app_cfg is not None:
                section_attr = ns_to_field(ns)
                if hasattr(app_cfg, section_attr):
                    section = getattr(app_cfg, section_attr)
                    if section is not None:
                        data = section if isinstance(section, dict) else section.model_dump()
                        filtered = {k: v for k, v in data.items() if k in sig.parameters}
                        return fn(*args, **filtered, **kwargs)

            return fn(*args, **kwargs)

        return wrapper

    return decorator
