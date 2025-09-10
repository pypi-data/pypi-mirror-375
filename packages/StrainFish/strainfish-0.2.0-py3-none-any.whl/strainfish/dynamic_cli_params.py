"""
StrainFish CLI interface builder class.

Kranti Konganti
(C) HFP, FDA.
"""

import os
from dataclasses import fields, is_dataclass
from typing import Any, Callable, Dict, Optional, Type

import click
from rich import box
from rich.table import Table as T

from .logging_utils import log


def _click_type(py_type: type) -> click.ParamType:
    """
    Map Python type annotations to corresponding Click parameter types.

    This internal helper function serves as a bridge between Python's type
    system and Click's command-line interface framework. It translates common
    Python data types into appropriate Click parameter types for CLI argument
    parsing and validation. This ensures consistent type handling across the
    StrainFish command-line interface.

    Args:
        py_type (type): The Python type annotation to be mapped to a Click
            parameter type. Supported types include int, float, str, bool,
            and os.PathLike. Other types default to string parameters.

    Returns:
        click.ParamType: A Click parameter type instance corresponding to the
            input Python type. For example, int maps to click.INT, str maps
            to click.STRING, etc. Unsupported types default to click.STRING.

    Raises:
        None: This function handles all supported types internally and provides
            sensible defaults for unsupported types.
    """
    mapping = {
        int: click.INT,
        float: click.FLOAT,
        str: click.STRING,
        bool: click.BOOL,
        os.PathLike: click.Path,
    }
    return mapping.get(py_type, click.STRING)


def add_params_from_dataclass(
    cfg_cls: Type,
    *,
    prefix: str = "",
    expose_none: bool = False,
) -> Callable[[Callable], Callable]:
    """
    Return a decorator that injects a Click option for each field of `cfg_cls`.

    Args:
        cfg_cls : dataclass
            The configuration class whose fields we want to expose.
        prefix : str, optional
            Prefix added to the command-line flag name (default = no prefix).
        expose_none : bool, optional
            By default we set default=None so we can tell whether the user
            passed the flag.
    """
    if not is_dataclass(cfg_cls):
        log.error(TypeError(f"{cfg_cls!r} is not a dataclass"))

    def decorator(method: Callable) -> Callable:
        for f in reversed(fields(cfg_cls)):
            flag_name = f"--{prefix}{f.name.replace('_', '-')}"
            click_type = _click_type(f.type)

            help_msg = f.metadata.get(
                "help",
                (
                    f"XGBoost parameter `{f.name}` (default: {f.default})"
                    if cfg_cls.__name__ == "XGBoostConfig"
                    else f"RandomForest parameter `{f.name}` (default: {f.default})"
                ),
            )

            default_val = None if not expose_none else f.default

            method = click.option(
                flag_name,
                default=default_val,
                type=click_type,
                show_default=False,
                help=help_msg,
                hidden=True,
            )(method)
        return method

    return decorator


def build_params(cfg_cls: Type, raw_kwargs: Dict[str, Any], prefix: str = "") -> Any:
    """
    Given a dataclass type and the raw **kwargs coming from Click,
    return a fully populated config object.

    Steps:
        1. Drop keys whose value is None, those were not supplied on the CLI.
        2. Initialise the dataclass with the remaining key/value pairs.
        3. (Optional) run any cross parameter validation and error out.
    """
    supplied = {
        k.replace(prefix, ""): v
        for k, v in raw_kwargs.items()
        if k.startswith(prefix) and v is not None
    }
    cfg = cfg_cls(**supplied)

    if cfg_cls.__name__ == "XGBoostConfig":
        if cfg.device not in {"cpu", "cuda"}:
            raise click.BadParameter("device must be 'cpu' or 'cuda'")
        # if cfg.tree_method == "hist" and cfg.device != "cuda":
        #     raise click.BadParameter("tree_method='hist' only works when device='cuda'")

    elif cfg_cls.__name__ == "RandomForestConfig":
        if int(cfg.n_estimators) <= 0:
            raise click.BadParameter("--rf-n-estimators must be > 0")
        if cfg.max_depth is not None and int(cfg.max_depth) <= 0:
            raise click.BadParameter("--rf-max-depth must be > 0 or None")

    return cfg


def fields2table(dataclass_type, title: str, prefix: Optional[str] = None) -> T:
    """
    Render the fields of a dataclass as a Rich Table.

    Args:
        dataclass_type : type
            The dataclass whose fields you want to display.
        title : str
            A short title that will appear above the table.
    """

    # table = T(title=f"{title} hyper-parameters")
    table = T(
        box=box.ROUNDED,
        border_style="dim white",
        show_edge=False,
        show_lines=False,
    )
    table.add_column("StrainFish Parameter", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Default", style="green")
    table.add_column("Description", style="yellow")

    if prefix is not None:
        prefix += "-"

    for f in dataclass_type.__dataclass_fields__.values():
        name = f.name
        msg = f.metadata["help"]

        default = (
            "None"
            if f.default is None
            or f.default
            is dataclass_type.__dict__["__dataclass_fields__"][name].default_factory
            else f.default
        )
        table.add_row(
            f"--{prefix}{name.replace('_', '-')}",
            str(f.type),
            str(default),
            f"{msg}",
        )

    return table
