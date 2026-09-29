"""
Unit tests for CLI parser and main entrypoint.
"""

from costguard.cli import create_parser, main


def test_cli_parser_help():
    parser = create_parser()
    assert parser.prog == "costguard"


def test_cli_main_plan_create(capsys):
    exit_code = main(["--plan", "test-plans/plan_create.json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "CostGuard" in captured.out
    assert "Monthly Cost Summary" in captured.out


def test_cli_main_missing_file():
    exit_code = main(["--plan", "non_existent_plan.json"])
    assert exit_code == 1


def test_cli_guardrail_breach_strict():
    exit_code = main(["--plan", "test-plans/plan_create.json", "--guardrail-limit", "10.0", "--strict"])
    assert exit_code == 1
