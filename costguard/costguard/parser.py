"""
Terraform plan JSON parser module for CostGuard.
Extracts resource changes, actions, and attributes from standard Terraform JSON output.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


def parse_plan(plan_path: str) -> Dict[str, Any]:
    """
    Parse a Terraform plan JSON file and extract structured resource changes.

    Args:
        plan_path: Path to the Terraform plan JSON file.

    Returns:
        Dict containing summary of planned additions, deletions, updates, and resource list.

    Raises:
        FileNotFoundError: If the specified plan file does not exist.
        ValueError: If the file is not valid JSON or lacks Terraform format_version.
    """
    path = Path(plan_path)
    if not path.exists():
        raise FileNotFoundError(f"Plan file not found: {plan_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Invalid Terraform plan format: expected JSON object.")

    resource_changes = data.get("resource_changes", [])
    
    parsed_resources = []
    summary = {"create": 0, "delete": 0, "update": 0, "no-op": 0}

    for resource in resource_changes:
        r_type = resource.get("type", "")
        r_name = resource.get("name", "")
        r_address = resource.get("address", f"{r_type}.{r_name}")
        change = resource.get("change", {})
        actions = change.get("actions", [])

        action_type = _determine_action_type(actions)
        if action_type in summary:
            summary[action_type] += 1

        parsed_resources.append({
            "address": r_address,
            "type": r_type,
            "name": r_name,
            "action": action_type,
            "actions": actions,
            "before": change.get("before"),
            "after": change.get("after"),
        })

    return {
        "format_version": data.get("format_version", "1.0"),
        "terraform_version": data.get("terraform_version", "unknown"),
        "summary": summary,
        "resources": parsed_resources,
    }


def _determine_action_type(actions: List[str]) -> str:
    """Helper to classify action array into create, delete, update, or no-op."""
    if actions == ["create"]:
        return "create"
    elif actions == ["delete"]:
        return "delete"
    elif actions == ["update"] or ("create" in actions and "delete" in actions):
        return "update"
    elif actions == ["no-op"] or not actions:
        return "no-op"
    return "update"
