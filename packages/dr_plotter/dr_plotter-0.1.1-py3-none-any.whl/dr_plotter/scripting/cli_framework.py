from __future__ import annotations

from dataclasses import MISSING, fields
from pathlib import Path
from typing import Any, Callable, TypeVar, Union, get_args, get_origin

import click
import yaml

from dr_plotter.configs import (
    FacetingConfig,
    LayoutConfig,
    LegendConfig,
    PlotConfig,
    StyleConfig,
)
from dr_plotter.scripting.utils import convert_cli_value_to_type, parse_key_value_args

F = TypeVar("F", bound=Callable[..., Any])


def infer_click_type(field_type: type, field_default: Any = None) -> Any:
    origin = get_origin(field_type)
    args = get_args(field_type)

    if origin is Union:
        non_none_types = [arg for arg in args if arg is not type(None)]
        if non_none_types:
            return non_none_types[0]
        return str

    if origin is tuple and args:
        return tuple(args)

    if field_type is bool:
        return bool
    if field_type is int:
        return int
    if field_type is float:
        return float
    if field_type is str:
        return str

    return str


def generate_help_text(field: Any) -> str:
    field_name = field.name.replace("_", " ")
    return f"{field_name} parameter"


def add_options_from_config(
    config_class: type, skip_fields: set[str] | None = None
) -> Callable[[F], F]:
    def decorator(f: F) -> F:
        skip_fields_set = skip_fields or set()

        for field in fields(config_class):
            if field.name in skip_fields_set:
                continue

            option_name = f"--{field.name.replace('_', '-')}"
            click_type = infer_click_type(field.type, field.default)
            help_text = generate_help_text(field)

            if field.type is bool and field.default is not MISSING:
                if field.default:
                    no_option_name = f"--no-{field.name.replace('_', '-')}"
                    f = click.option(
                        no_option_name,
                        field.name,
                        flag_value=False,
                        default=field.default,
                        help=f"Disable {help_text.lower()}",
                    )(f)
                else:
                    f = click.option(
                        option_name,
                        field.name,
                        flag_value=True,
                        default=field.default,
                        help=f"Enable {help_text.lower()}",
                    )(f)
            elif field.default is not MISSING:
                f = click.option(
                    option_name, type=click_type, default=field.default, help=help_text
                )(f)
            else:
                f = click.option(option_name, type=click_type, help=help_text)(f)
        return f

    return decorator


def add_cli_only_options() -> Callable[[F], F]:
    def decorator(f: F) -> F:
        f = click.option("--save-dir", help="Directory to save plots")(f)
        f = click.option(
            "--pause", type=int, default=5, help="Display duration in seconds"
        )(f)
        f = click.option(
            "--config", type=click.Path(exists=True), help="YAML configuration file"
        )(f)
        return f

    return decorator


class CLIConfig:
    def __init__(self, config_data: dict[str, Any] | None = None) -> None:
        self.data = config_data or {}

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> CLIConfig:
        if isinstance(config_path, str):
            config_path = Path(config_path)
        assert config_path.exists(), f"Config file not found: {config_path}"
        assert config_path.suffix == ".yaml", "Config file must be a YAML file"
        with config_path.open() as f:
            data = yaml.safe_load(f)
        return cls(data)

    @classmethod
    def load_or_default(cls, kwargs: dict[str, Any]) -> CLIConfig:
        config_path = kwargs.pop("config", None)
        return cls.from_yaml(config_path) if config_path else cls()

    def merge_with_cli_args(self, cli_args: dict[str, Any]) -> dict[str, Any]:
        merged = {**self.data}
        merged.update(
            {key: value for key, value in cli_args.items() if value is not None}
        )
        return merged


def validate_layout_options(ctx: click.Context, **kwargs: Any) -> None:
    rows_by = kwargs.get("rows_by")
    cols_by = kwargs.get("cols_by")
    wrap_by = kwargs.get("wrap_by")

    if wrap_by is not None and (rows_by is not None or cols_by is not None):
        raise click.UsageError(
            "Cannot combine --wrap-by with --rows-by or --cols-by. Use either"
            " explicit grid (--rows-by + --cols-by) or wrapping (--wrap-by)."
        )


def build_faceting_config(
    kwargs: dict[str, Any],
) -> tuple[FacetingConfig, dict[str, Any]]:
    faceting_fields = {f.name for f in fields(FacetingConfig)}
    relevant_kwargs = {k: v for k, v in kwargs.items() if k in faceting_fields}
    remaining_kwargs = {k: v for k, v in kwargs.items() if k not in faceting_fields}

    def parse_dimension_value(value: Any) -> Any:
        if isinstance(value, dict):
            return value
        elif isinstance(value, (list, tuple)) and value:
            return parse_key_value_args(value)
        else:
            return None

    if "fixed" in relevant_kwargs:
        relevant_kwargs["fixed"] = parse_dimension_value(relevant_kwargs["fixed"])
    if "order" in relevant_kwargs:
        relevant_kwargs["order"] = parse_dimension_value(relevant_kwargs["order"])
    if "exclude" in relevant_kwargs:
        relevant_kwargs["exclude"] = parse_dimension_value(relevant_kwargs["exclude"])

    if "no_auto_titles" in remaining_kwargs:
        relevant_kwargs["auto_titles"] = not remaining_kwargs.pop(
            "no_auto_titles", False
        )

    faceting_config = FacetingConfig(**relevant_kwargs)
    return faceting_config, remaining_kwargs


def build_layout_config(kwargs: dict[str, Any]) -> tuple[LayoutConfig, dict[str, Any]]:
    layout_fields = {f.name: f.type for f in fields(LayoutConfig)}
    relevant_kwargs = {k: v for k, v in kwargs.items() if k in layout_fields}
    remaining_kwargs = {k: v for k, v in kwargs.items() if k not in layout_fields}

    converted_kwargs = {}
    for key, value in relevant_kwargs.items():
        field_type = layout_fields.get(key)
        if field_type:
            converted_kwargs[key] = convert_cli_value_to_type(value, field_type)
        else:
            converted_kwargs[key] = value

    layout_config = LayoutConfig(**converted_kwargs)
    return layout_config, remaining_kwargs


def build_legend_config(kwargs: dict[str, Any]) -> tuple[LegendConfig, dict[str, Any]]:
    legend_fields = {f.name for f in fields(LegendConfig)}
    relevant_kwargs = {k: v for k, v in kwargs.items() if k in legend_fields}
    remaining_kwargs = {k: v for k, v in kwargs.items() if k not in legend_fields}

    legend_config = LegendConfig(**relevant_kwargs)
    return legend_config, remaining_kwargs


def build_style_config(kwargs: dict[str, Any]) -> tuple[StyleConfig, dict[str, Any]]:
    style_fields = {f.name for f in fields(StyleConfig)}
    relevant_kwargs = {k: v for k, v in kwargs.items() if k in style_fields}
    remaining_kwargs = {k: v for k, v in kwargs.items() if k not in style_fields}

    style_config = StyleConfig(**relevant_kwargs)
    return style_config, remaining_kwargs


def build_configs(kwargs: dict[str, Any]) -> tuple[PlotConfig, dict[str, Any]]:
    faceting_config, unused = build_faceting_config(kwargs)
    layout_config, unused = build_layout_config(unused)
    legend_config, unused = build_legend_config(unused)
    style_config, unused = build_style_config(unused)

    plot_config = PlotConfig(
        layout=layout_config,
        legend=legend_config,
        style=style_config if style_config.theme else None,
        faceting=faceting_config,
    )

    return plot_config, unused


def validate_unused_parameters(
    unused_kwargs: dict[str, Any], allowed_params: set[str] | None = None
) -> None:
    if unused_kwargs:
        allowed_set = allowed_params or set()
        unexpected_params = {k for k in unused_kwargs if k not in allowed_set}
        if unexpected_params:
            unused_params = ", ".join(unexpected_params)
            raise click.UsageError(f"Unknown parameters: {unused_params}")


def build_plot_config(
    config: CLIConfig, theme: str | None = None, **cli_overrides: Any
) -> PlotConfig:
    merged = config.merge_with_cli_args(cli_overrides)

    return PlotConfig(
        layout=LayoutConfig(
            rows=merged.get("rows", 1),
            cols=merged.get("cols", 1),
            figsize=merged.get("figsize", (12.0, 8.0)),
            tight_layout=merged.get("tight_layout", True),
            tight_layout_pad=merged.get("tight_layout_pad", 1.0),
        ),
        legend=LegendConfig(legend_strategy=merged.get("legend_strategy", "subplot")),
        style=StyleConfig(theme=theme) if theme else None,
    )


def dimensional_plotting_cli(skip_fields: set[str] | None = None) -> Callable[[F], F]:
    def decorator(f: F) -> F:
        f = add_cli_only_options()(f)
        f = add_options_from_config(StyleConfig, skip_fields)(f)
        f = add_options_from_config(LegendConfig, skip_fields)(f)
        f = add_options_from_config(LayoutConfig, skip_fields)(f)
        f = add_options_from_config(FacetingConfig, skip_fields)(f)
        return f

    return decorator
