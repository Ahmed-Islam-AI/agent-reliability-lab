"""Tool: look up one of the customer's orders."""

from pydantic import BaseModel, ConfigDict

from agentlab.domains.support.support_environment import SupportEnvironment
from agentlab.domains.support.support_types import OrderId
from agentlab.domains.support.tools.order_access import find_accessible_order
from agentlab.models.attempt_context import AttemptContext
from agentlab.models.tool_result import ToolResult
from agentlab.models.tool_spec import ToolSpec


class GetOrderArgs(BaseModel):
    """Arguments of `get_order`."""

    model_config = ConfigDict(extra="forbid", strict=True)

    order_id: OrderId


def get_order(
    environment: SupportEnvironment, args: GetOrderArgs, context: AttemptContext
) -> ToolResult:
    """Return the order with its refunded and still-refundable amounts."""
    found = find_accessible_order(environment, args.order_id, context.user_id)
    if isinstance(found, ToolResult):
        return found
    details = found.model_dump(mode="json", exclude={"id", "customer_id"})
    return ToolResult.ok(
        {
            "order_id": found.id,
            **details,
            "refunded_amount_minor": environment.refunded_total(found.id),
            "refundable_amount_minor": environment.refundable_balance(found),
        }
    )


GET_ORDER = ToolSpec(
    name="get_order",
    description="Look up one of the customer's orders by its id (e.g. ord_1042).",
    args_model=GetOrderArgs,
    handler=get_order,
)
