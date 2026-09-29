"""
Guardrail evaluation module for CostGuard.
Enforces cost threshold limits and policy compliance.
"""

from typing import Dict, Any, Optional


def evaluate_guardrails(impact_report: Dict[str, Any], limit: Optional[float] = None) -> bool:
    """
    Evaluate if predicted monthly cost change complies with cost guardrail policies.

    Args:
        impact_report: Cost calculation dictionary returned by calculate_cost_impact.
        limit: Optional maximum allowed monthly cost delta.

    Returns:
        True if cost increase is within allowed limit (or no limit set), False if breached.
    """
    if limit is None:
        return True

    net_delta = impact_report.get("net_monthly_delta", 0.0)
    
    # If cost increase is greater than defined threshold limit
    if net_delta > limit:
        return False

    return True
