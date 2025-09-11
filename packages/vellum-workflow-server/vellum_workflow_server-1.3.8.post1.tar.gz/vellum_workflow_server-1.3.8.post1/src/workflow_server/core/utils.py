from datetime import datetime
import os
from uuid import uuid4
from typing import Optional

from vellum import ApiVersionEnum, Vellum, VellumEnvironment
from workflow_server.config import IS_VPC, VELLUM_API_URL_HOST, VELLUM_API_URL_PORT
from workflow_server.core.events import VembdaExecutionFulfilledBody, VembdaExecutionFulfilledEvent
from workflow_server.core.workflow_executor_context import BaseExecutorContext


def _create_vembda_rejected_event_base(
    executor_context: Optional[BaseExecutorContext], error_message: str
) -> VembdaExecutionFulfilledEvent:
    if executor_context:
        trace_id = executor_context.trace_id
        span_id = executor_context.execution_id
        container_overhead_latency = executor_context.container_overhead_latency
    else:
        trace_id = uuid4()
        span_id = uuid4()
        container_overhead_latency = None

    return VembdaExecutionFulfilledEvent(
        id=uuid4(),
        timestamp=datetime.now(),
        trace_id=trace_id,
        span_id=span_id,
        body=VembdaExecutionFulfilledBody(
            exit_code=-1,
            stderr=error_message,
            container_overhead_latency=container_overhead_latency,
        ),
        parent=None,
    )


def create_vembda_rejected_event(executor_context: Optional[BaseExecutorContext], error_message: str) -> dict:
    return _create_vembda_rejected_event_base(executor_context, error_message).model_dump(mode="json")


def serialize_vembda_rejected_event(executor_context: Optional[BaseExecutorContext], error_message: str) -> str:
    return _create_vembda_rejected_event_base(executor_context, error_message).model_dump_json()


def is_events_emitting_enabled(executor_context: Optional[BaseExecutorContext]) -> bool:
    if not executor_context:
        return False

    if not executor_context.feature_flags:
        return False

    return executor_context.feature_flags.get("vembda-event-emitting-enabled") or False


def create_vellum_client(
    api_key: str,
    api_version: Optional[ApiVersionEnum] = None,
) -> Vellum:
    """
    Create a VellumClient with proper environment configuration.

    Args:
        api_key: The API key for the Vellum client
        api_version: Optional API version to use

    Returns:
        Configured Vellum client instance

    Note: Ideally we replace this with `vellum.workflows.vellum_client.create_vellum_client`
    """
    if IS_VPC:
        environment = VellumEnvironment(
            default=os.getenv("VELLUM_DEFAULT_API_URL", VellumEnvironment.PRODUCTION.default),
            documents=os.getenv("VELLUM_DOCUMENTS_API_URL", VellumEnvironment.PRODUCTION.documents),
            predict=os.getenv("VELLUM_PREDICT_API_URL", VellumEnvironment.PRODUCTION.predict),
        )
    elif os.getenv("USE_LOCAL_VELLUM_API") == "true":
        VELLUM_API_URL = f"http://{VELLUM_API_URL_HOST}:{VELLUM_API_URL_PORT}"
        environment = VellumEnvironment(
            default=VELLUM_API_URL,
            documents=VELLUM_API_URL,
            predict=VELLUM_API_URL,
        )
    else:
        environment = VellumEnvironment.PRODUCTION

    return Vellum(
        api_key=api_key,
        environment=environment,
        api_version=api_version,
    )
