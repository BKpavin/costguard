import argparse
import sys
from typing import List, Optional
from costguard import __version__
from costguard.parser import parse_plan
from costguard.calculator import calculate_cost_impact
from costguard.guardrail import evaluate_guardrails
from costguard.output import render_cost_report


def create_parser() -> argparse.ArgumentParser:
    """Construct and return the command-line argument parser for CostGuard."""
    parser = argparse.ArgumentParser(
        prog="costguard",
        description="CostGuard: Predict monthly Azure infrastructure cost impacts from Terraform plan JSON files before deployment.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  costguard --plan test-plans/plan_create.json
  costguard --plan tfplan.json --guardrail-limit 500 --strict
  costguard -p plan_update.json --currency EUR
"""
    )

    parser.add_argument(
        "-p", "--plan",
        type=str,
        default="plan.json",
        metavar="FILE",
        help="Path to Terraform plan JSON file (default: plan.json)"
    )

    parser.add_argument(
        "--currency",
        type=str,
        default="USD",
        help="Currency code for pricing calculation (default: USD)"
    )

    parser.add_argument(
        "--guardrail-limit",
        type=float,
        default=None,
        metavar="AMOUNT",
        help="Maximum acceptable monthly cost increase threshold"
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero exit status if guardrail limit is breached"
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    return parser


def main(sys_args: Optional[List[str]] = None) -> int:
    """
    Main entry point for CostGuard CLI application.
    
    Args:
        sys_args: Optional command line arguments list (defaults to sys.argv[1:])

    Returns:
        Exit status code (0 for success, non-zero for errors or guardrail breaches)
    """
    parser = create_parser()
    args = parser.parse_args(sys_args)

    # Print initial CLI status
    print(f"CostGuard v{__version__} - Azure Infrastructure Cost Impact Predictor")
    print(f"Analyzing Terraform plan: {args.plan}")
    
    try:
        plan_data = parse_plan(args.plan)
        impact = calculate_cost_impact(plan_data, currency=args.currency)
        passed_guardrails = evaluate_guardrails(impact, limit=args.guardrail_limit)
        render_cost_report(impact, guardrail_limit=args.guardrail_limit)

        if args.strict and not passed_guardrails:
            print("\nGuardrail policy failed: Cost increase exceeds threshold.")
            return 1

        return 0

    except FileNotFoundError:
        print(f"Error: Terraform plan file '{args.plan}' not found.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error executing CostGuard: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
