import asyncio
import re
import time
import warnings
from contextlib import contextmanager
from functools import partial, wraps
from typing import Literal

from httpx import AsyncClient, Request, Response
from prometheus_client import Counter, Histogram
from prometheus_client import generate_latest, REGISTRY, CONTENT_TYPE_LATEST
from prometheus_client.metrics import MetricWrapperBase

COMMON_METRIC_TEMPLATE = "genapp_{}"

_metric: "CommonMetrics" = None


def build_prometheus_metrics(project_name: str, env: Literal["dev", "preprod", "prod"]) -> "CommonMetrics":
    global _metric

    if env not in ("dev", "preprod", "prod"):
        raise ValueError(f"No valid env value for metrics: {env}")

    _metric = CommonMetrics(project_name, env)

    return _metric


class SetDefaultLabelsMixin:
    """
    Атрибут env и app есть у всех метрик, чтобы не загрязнять код установкой этого атрибута,
    этот класс миксин подставляет их для всех.
    Но метод .labels() все равно надо вызывать!
    """

    def __init__(self, project_name: str, env: Literal["dev", "preprod", "prod"]):
        self.env = env
        self.project_name = project_name

    def __getattribute__(self, item):
        attr = super().__getattribute__(item)

        if isinstance(attr, MetricWrapperBase):
            # Проверяем, поддерживает ли метрика атрибут "app".
            if hasattr(attr, "_labelnames") and "app" in attr._labelnames:  # noqa: SLF001
                attr.labels = partial(attr.labels, env=self.env, app=self.project_name)
            else:
                attr.labels = partial(attr.labels, env=self.env)

        return attr


class CommonMetrics(SetDefaultLabelsMixin):
    # Common Metrics:
    HTTP_REQUESTS = Counter(
        COMMON_METRIC_TEMPLATE.format("http_requests_total"),
        "Total number of HTTP requests",
        ["method", "status", "resource", "app_type", "env", "app"],
    )
    HTTP_REQUEST_DURATION = Histogram(
        COMMON_METRIC_TEMPLATE.format("http_request_duration_sec"),
        "HTTP request latency in seconds",
        ["method", "status", "resource", "app_type", "env", "app"],
        buckets=[0.1, 0.5, 1, 3, 5, 10, 20, 30, 60, 120, 300, 600, 3600, float("inf")],
    )
    HTTP_REQUEST_DURATION_TOTAL = Counter(
        COMMON_METRIC_TEMPLATE.format("http_request_duration_sec_total"),
        "Total duration of HTTP request in seconds",
        ["method", "status", "resource", "app_type", "env", "app"],
    )
    HTTP_REQUEST_SIZE = Histogram(
        COMMON_METRIC_TEMPLATE.format("http_request_size_bytes"),
        "HTTP request or response size in bytes",
        ["resource", "status", "method", "direction", "app_type", "env", "app"],
        buckets=[100, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, float("inf")],
    )
    HTTP_REQUEST_SIZE_TOTAL = Counter(
        COMMON_METRIC_TEMPLATE.format("http_request_size_bytes_total"),
        "Total size of HTTP request or response in bytes",
        ["resource", "status", "method", "direction", "app_type", "env", "app"],
    )

    ACTION_COUNT = Counter(
        COMMON_METRIC_TEMPLATE.format("action_count_total"),
        "Total action requests",
        ["name", "status", "env", "app"],
    )
    ACTION_DURATION = Histogram(
        COMMON_METRIC_TEMPLATE.format("action_duration_sec"),
        "Action request latency",
        ["name", "env", "app"],
        buckets=[0.01, 0.1, 0.5, 1, 2, 5, 10, 20, 30, 60, 120, 600, 3600, 3600 * 12, 3600 * 24, float("inf")],
    )
    ACTION_SIZE = Counter(
        COMMON_METRIC_TEMPLATE.format("action_size_total"),
        "Total event size",
        ["name", "env", "app"],
    )


@contextmanager
def action_tracking(name: str):
    """
    Отслеживание кол-ва вызова и времени выполнения секций кода с отслеживаниием появления ошибок.
    """
    if _metric:
        begin = time.perf_counter()
        try:
            # Наружу передается класс, через который можно зафиксировать дополнительные метрики.
            class TrackSize:
                @staticmethod
                def size(size):
                    _metric.ACTION_SIZE.labels(name=name).inc(size)

            yield TrackSize

        except Exception:
            _metric.ACTION_COUNT.labels(name=name, status="error").inc()
            raise

        else:
            _metric.ACTION_COUNT.labels(name=name, status="ok").inc()

        finally:
            duration = round(time.perf_counter() - begin, 3)
            _metric.ACTION_DURATION.labels(name=name).observe(duration)
    else:

        class TrackSize:
            @staticmethod
            def size(size):
                pass

        yield TrackSize
        warnings.warn("Prometheus metrics not initialized", UserWarning)


def action_tracking_decorator(name: str):
    """
    Отслеживание кол-ва вызова и времени выполнения функций и корутин.
    """

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                with action_tracking(name):
                    return await func(*args, **kwargs)

            return async_wrapper

        @wraps(func)
        def wrapper(*args, **kwargs):
            with action_tracking(name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def http_tracking(
    app_type: str, resource: str, method: str, response_size: int, status_code: int, duration: float, request_size: int
):
    if _metric:
        resource = resource.strip("/")

        _metric.HTTP_REQUESTS.labels(method=method, resource=resource, status=status_code, app_type=app_type).inc()
        _metric.HTTP_REQUEST_DURATION.labels(
            method=method, resource=resource, status=status_code, app_type=app_type
        ).observe(duration)
        _metric.HTTP_REQUEST_DURATION_TOTAL.labels(
            method=method, resource=resource, status=status_code, app_type=app_type
        ).inc(duration)
        _metric.HTTP_REQUEST_SIZE.labels(
            method=method, resource=resource, status=status_code, direction="in", app_type=app_type
        ).observe(request_size)
        _metric.HTTP_REQUEST_SIZE.labels(
            method=method, resource=resource, status=status_code, direction="out", app_type=app_type
        ).observe(response_size)
        _metric.HTTP_REQUEST_SIZE_TOTAL.labels(
            method=method, resource=resource, status=status_code, direction="in", app_type=app_type
        ).inc(request_size)
        _metric.HTTP_REQUEST_SIZE_TOTAL.labels(
            method=method, resource=resource, status=status_code, direction="out", app_type=app_type
        ).inc(response_size)

    else:
        warnings.warn("Prometheus metrics not initialized", UserWarning)


class HttpxClientWithMonitoring(AsyncClient):
    """Custom async httpx client that collects metrics for HTTP requests."""

    name_for_monitoring = None

    def clear_resource_path(self, resource: str):
        """
        Надо очищать URL ресурсов от значений идентификаторов, которые мешают группировки запросов.
        По умолчанию на всякий случай очищаются числа, если кто-то не позаботится об очистке самостоятельно.
        """
        resource = re.sub(r"/\d+", "/{int}", resource)
        resource = re.sub(r"\d{2,}", "{int}", resource)

        return resource

    async def send(self, request: Request, **kwargs) -> Response:
        if not self.name_for_monitoring:
            raise NotImplementedError("Not set name http requests for monitoring")

        response = await super().send(request, **kwargs)

        if _metric:
            request_size = int(request.headers.get("content-length", len(getattr(request, "content", ""))))
            response_size = int(response.headers.get("content-length", len(getattr(response, "content", ""))))
            resource = self.clear_resource_path(request.url.path)

            http_tracking(
                app_type=self.name_for_monitoring,
                resource=resource,
                method=request.method,
                response_size=response_size,
                status_code=response.status_code,
                duration=response.elapsed.total_seconds(),
                request_size=request_size,
            )

        else:
            warnings.warn("Prometheus metrics not initialized", UserWarning)

        return response


async def fastapi_tracking_middleware(request: Request, call_next):
    begin = time.perf_counter()
    response = await call_next(request)

    if _metric:
        process_time = round(time.perf_counter() - begin, 3)

        resource = re.sub(r"/eapi/servisy-raboty-llm-bigdata[^/]+", "", request.url.path)

        if resource not in ("/docs", "/openapi.json", "/health", "/prometheus", "/favicon.ico"):
            resource = re.sub(r"/\d+", "/{int}", resource)
            resource = re.sub(r"\d{2,}", "{int}", resource)

            http_tracking(
                app_type="app_api",
                resource=resource,
                method=request.method,
                status_code=response.status_code,
                duration=process_time,
                response_size=int(response.headers.get("content-length", 0)),
                request_size=int(request.headers.get("content-length", 0)),
            )

    else:
        warnings.warn("Prometheus metrics not initialized", UserWarning)

    return response


async def fastapi_endpoint_for_prometheus():
    from starlette.responses import Response

    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
