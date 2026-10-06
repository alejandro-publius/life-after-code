"""Night Orders: before bed, the on-call engineer signs what the agent may do alone tonight.

This package is the part that decides what is true. It never calls a model. The model drafts
orders at dusk and names an order (or declines) at night; code checks every word against the
signed file before anything changes in production.
"""

from .decide import Act, Ask, Night, StandDown, Waiting, Wake, approve_suggestion, check_request, recheck, triage
from .ledger import Ledger
from .model import Action, Alert, Condition, OnCall, Order, Orders, Signature, Targets
from .notes import Malformed, Request, parse_request, render_request
from .orders import OrdersError, load_context, parse_oncall, parse_orders, parse_targets, signature_problems
from .signals import Metrics, condition_holds

__all__ = [
    "Act", "Action", "Alert", "Ask", "Condition", "Ledger", "Malformed", "Metrics", "Night", "OnCall", "Order",
    "Orders", "OrdersError", "Request", "Signature", "StandDown", "Targets", "Waiting", "Wake",
    "approve_suggestion", "check_request", "condition_holds", "load_context", "parse_oncall", "parse_orders",
    "parse_request", "parse_targets", "recheck", "render_request", "signature_problems", "triage",
]
