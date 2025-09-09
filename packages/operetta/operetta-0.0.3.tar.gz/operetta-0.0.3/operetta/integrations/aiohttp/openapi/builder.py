import logging
import re
from collections import defaultdict
from dataclasses import dataclass, make_dataclass
from functools import partial
from pathlib import Path
from typing import Any, Callable, Iterable, Literal, Sequence, Type, Union

import aiohttp.web
from apispec.yaml_utils import dict_to_yaml
from openapify.core.base_plugins import BaseSchemaPlugin
from openapify.core.const import (
    DEFAULT_OPENAPI_VERSION,
    DEFAULT_SPEC_TITLE,
    DEFAULT_SPEC_VERSION,
)
from openapify.core.models import RouteDef
from openapify.ext.web.aiohttp import AioHttpRouteDef, build_spec

# from voice_skills_answers.answers import Answer

# from proxy_app.openapi.http_error_analyzer import HTTPErrorAnalyzer
# from proxy_app.routes import get_routes
# from proxy_app.web_apierr import APIError, registry

COLLECTED_TAGS: set[str] = set()
PATH_PREFIX = re.compile("/([^/]+)")
# HTTP_EXCEPTION_MAP = {cls.__name__: cls for cls in registry.get_all()}

logger = logging.getLogger(__name__)


def is_http_exception(module: str, cls_name: str) -> bool:
    return module == "proxy_app.web_apierr" and cls_name == "APIError"


# def get_http_exception_cls(name: str) -> Type[APIError]:
#     return HTTP_EXCEPTION_MAP[name]


# http_error_analyzer = HTTPErrorAnalyzer(
#     include_packages={"proxy_app"},
#     is_http_exception=is_http_exception,
# )


@dataclass
class ErrorResponse:
    code: int
    error: str
    qid: str
    reason: str


# def add_handler_error_responses(handler: Any) -> None:
#     logger.debug(
#         f"Analyze handler {handler.__module__} -> {handler.__qualname__}"
#     )
#     try:
#         exception_names = http_error_analyzer.get_exceptions(handler)
#         meta = getattr(handler, "__openapify__", [])
#         if not meta:
#             handler.__openapify__ = meta  # type: ignore[attr-defined]
#         exc_bodies: dict[int, dict[int, Any]] = defaultdict(dict)
#         exc_examples: dict[int, dict[str, dict[str, Any]]] = defaultdict(dict)
#         for exc_name in exception_names:
#             exc = get_http_exception_cls(exc_name)
#             exc_bodies[exc.http_status][exc.code] = make_dataclass(
#                 f"ErrorResponse_{exc.code}",
#                 (  # type: ignore[arg-type]
#                     ("code", Literal[exc.code]),
#                     ("error", Literal[f"{exc.code}:{exc.reason_format}"]),
#                     ("reason", Literal[exc.reason_format]),
#                 ),
#                 bases=(ErrorResponse,),
#             )
#             exc_examples[exc.http_status][
#                 f"{exc.code}:{exc.reason_format}"
#             ] = {
#                 "code": exc.code,
#                 "error": f"{exc.code}:{exc.reason_format}",
#                 "qid": "...",
#                 "reason": exc.reason_format,
#             }
#         for http_code, bodies in exc_bodies.items():
#             meta.append(
#                 (
#                     "response",
#                     {
#                         "body": Union[*(v for _, v in sorted(bodies.items()))],
#                         "http_code": http_code,
#                         "media_type": "application/json",
#                         "examples": dict(
#                             sorted(exc_examples[http_code].items())
#                         ),
#                     },
#                 ),
#             )
#     except Exception as e:
#         if handler.__module__.split(".")[0] == "voice_front":
#             logger.exception(
#                 f"Failed to analyze handler {handler.__module__} -> {handler.__qualname__}: %s",
#                 e,
#             )
#         else:
#             logger.warning(
#                 f"Skip failed to analyze handler {handler.__module__} "
#                 f"-> {handler.__qualname__}: %s",
#                 e,
#             )


def route_postprocessor(
    route: RouteDef, remove_prefix: str | None = None
) -> RouteDef | None:
    if remove_prefix and route.path.startswith(remove_prefix):
        route.path = route.path[len(remove_prefix) :] or "/"
    return route


# def route_postprocessor(
#     route: RouteDef, exclude_internal: bool = False
# ) -> Union[RouteDef, None]:
#     add_handler_error_responses(route.handler)
#     match = PATH_PREFIX.match(route.path)
#     if match:
#         tag = match.group(1)
#         if tag == "internal" and exclude_internal:
#             return None
#         # COLLECTED_TAGS.add(tag)
#         # if route.tags:
#         #     route.tags.append(tag)
#         # else:
#         #     route.tags = [tag]
#     return route


def rebuild_spec(
    routes: Iterable[AioHttpRouteDef],
    spec_path: Union[str, Path],
    title: str = DEFAULT_SPEC_TITLE,
    servers: Sequence[str] = ("http://127.0.0.1:8080",),
    tag_descriptions: dict[str, str] | None = None,
    tag_groups: dict[str, list[str]] | None = None,
    remove_path_prefix: str | None = None,
) -> None:
    if remove_path_prefix:
        remove_path_prefix = remove_path_prefix.rstrip("/")
    spec = build_spec(  # type: ignore[assignment]
        routes,
        title=title,
        version=DEFAULT_SPEC_VERSION,
        openapi_version=DEFAULT_OPENAPI_VERSION,
        servers=list(servers),
        route_postprocessor=partial(
            route_postprocessor, remove_prefix=remove_path_prefix
        ),
    )
    for tag in sorted(COLLECTED_TAGS):
        spec.tag({"name": tag})

    spec_dict = spec.to_dict()

    if tag_descriptions:
        spec_dict["tags"] = [
            {"name": tag_name, "description": tag_description}
            for tag_name, tag_description in tag_descriptions.items()
        ]
    if tag_groups:
        spec_dict["x-tagGroups"] = [
            {"name": group_name, "tags": group_tags}
            for group_name, group_tags in tag_groups.items()
        ]

    with open(spec_path, "w") as f:
        f.write(
            dict_to_yaml(spec_dict, yaml_dump_kwargs={"allow_unicode": True})
        )
