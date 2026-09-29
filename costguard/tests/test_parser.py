"""
Unit tests for Terraform plan JSON parser.
"""

from costguard.parser import parse_plan


def test_parse_plan_create():
    result = parse_plan("test-plans/plan_create.json")
    assert result["summary"]["create"] == 3
    assert len(result["resources"]) == 3


def test_parse_plan_delete():
    result = parse_plan("test-plans/plan_delete.json")
    assert result["summary"]["delete"] == 2


def test_parse_plan_update():
    result = parse_plan("test-plans/plan_update.json")
    assert result["summary"]["update"] == 1


def test_parse_plan_noise():
    result = parse_plan("test-plans/plan_noise.json")
    assert result["summary"]["create"] == 2
    assert result["summary"]["update"] == 1
