"""Night Orders: before bed, the on-call engineer signs what the agent may do alone tonight.

This package is the part that decides what is true. It never calls a model. The model drafts
orders at dusk and names an order (or declines) at night; code checks every word against the
signed file before anything changes in production.
"""

from .decide import (Act, Ask, Night, StandDown, Waiting, Wake, approve_suggestion, check_request, recheck,
                     standing_order, triage)
from .ledger import Ledger
from .model import Action, Alert, Change, Condition, OnCall, Order, Orders, Signature, Targets, describe_before
from .notes import Malformed, Request, parse_request, render_request
from .orders import OrdersError, load_context, parse_oncall, parse_orders, parse_targets, signature_problems
from .signals import Metrics, condition_holds

# The public repository the demo's "inspect the code" links point at. Change it once to the GitLab project
# when the submission repository exists, and every link in the demo follows.
REPO_URL = "https://github.com/alejandro-publius/life-after-code"

__all__ = [
    "REPO_URL",
    "Act", "Action", "Alert", "Ask", "Change", "Condition", "Ledger", "Malformed", "Metrics", "Night", "OnCall",
    "Order", "Orders", "OrdersError", "Request", "Signature", "StandDown", "Targets", "Waiting", "Wake",
    "approve_suggestion", "check_request", "condition_holds", "describe_before", "load_context", "parse_oncall",
    "parse_orders", "parse_request", "parse_targets", "recheck", "render_request", "signature_problems",
    "standing_order", "triage",
]
