"""
Cost calculator module for CostGuard.
Calculates monthly cost impact based on resource changes in Terraform plan.
"""

from typing import Dict, Any, List

HOURS_PER_MONTH = 730  # Standard average hours per month in cloud billing


def calculate_cost_impact(plan_data: Dict[str, Any], currency: str = "USD") -> Dict[str, Any]:
    """
    Calculate the monthly cost delta for all resources in a parsed Terraform plan.

    Args:
        plan_data: Dictionary returned by parse_plan containing resource changes.
        currency: Target currency code.

    Returns:
        Dict containing resource level details, total previous cost, total new cost, and net delta.
    """
    resources = plan_data.get("resources", [])
    itemized_impact: List[Dict[str, Any]] = []

    total_previous_monthly = 0.0
    total_new_monthly = 0.0

    for res in resources:
        action = res["action"]
        res_type = res["type"]
        res_name = res["name"]
        address = res["address"]

        # Default pricing mapping stub for common Azure resources
        previous_monthly = 0.0
        new_monthly = 0.0

        monthly_rate = _estimate_resource_monthly_cost(res_type, res.get("after") or res.get("before"))

        if action == "create":
            previous_monthly = 0.0
            new_monthly = monthly_rate
        elif action == "delete":
            previous_monthly = monthly_rate
            new_monthly = 0.0
        elif action == "update":
            old_rate = _estimate_resource_monthly_cost(res_type, res.get("before"))
            previous_monthly = old_rate
            new_monthly = monthly_rate
        else:  # no-op
            previous_monthly = monthly_rate
            new_monthly = monthly_rate

        delta = new_monthly - previous_monthly
        total_previous_monthly += previous_monthly
        total_new_monthly += new_monthly

        itemized_impact.append({
            "address": address,
            "type": res_type,
            "name": res_name,
            "action": action,
            "previous_monthly": round(previous_monthly, 2),
            "new_monthly": round(new_monthly, 2),
            "delta_monthly": round(delta, 2),
            "currency": currency,
        })

    net_monthly_delta = total_new_monthly - total_previous_monthly

    return {
        "currency": currency,
        "total_previous_monthly": round(total_previous_monthly, 2),
        "total_new_monthly": round(total_new_monthly, 2),
        "net_monthly_delta": round(net_monthly_delta, 2),
        "summary": plan_data.get("summary", {}),
        "itemized": itemized_impact
    }


def _estimate_resource_monthly_cost(resource_type: str, attributes: Any) -> float:
    """Helper to estimate baseline monthly cost based on resource type and attributes."""
    if not attributes or not isinstance(attributes, dict):
        return 0.0

    # Azure Linux/Windows VM estimation example
    if resource_type == "azurerm_linux_virtual_machine" or resource_type == "azurerm_windows_virtual_machine":
        size = attributes.get("size", "Standard_D2s_v3")
        sku_prices = {
            "Standard_B1s": 0.012 * HOURS_PER_MONTH,     # ~$8.76/mo
            "Standard_B2s": 0.0416 * HOURS_PER_MONTH,    # ~$30.37/mo
            "Standard_D2s_v3": 0.096 * HOURS_PER_MONTH,  # ~$70.08/mo
            "Standard_D4s_v3": 0.192 * HOURS_PER_MONTH,  # ~$140.16/mo
        }
        return sku_prices.get(size, 70.08)

    # Azure Managed Disk
    elif resource_type == "azurerm_managed_disk":
        disk_size_gb = attributes.get("disk_size_gb", 128)
        storage_account_type = attributes.get("storage_account_type", "Premium_LRS")
        per_gb_rate = 0.135 if "Premium" in storage_account_type else 0.05
        return round(disk_size_gb * per_gb_rate, 2)

    # Azure Storage Account
    elif resource_type == "azurerm_storage_account":
        account_tier = attributes.get("account_tier", "Standard")
        return 20.00 if account_tier == "Standard" else 100.00

    # Azure App Service Plan
    elif resource_type == "azurerm_service_plan":
        sku_name = attributes.get("sku_name", "P1v2")
        sku_prices = {"B1": 13.0, "S1": 73.0, "P1v2": 146.0, "P2v2": 292.0}
        return sku_prices.get(sku_name, 73.0)

    # Free/non-cost resources or unknown resources
    return 0.0
