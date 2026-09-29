# CostGuard

**CostGuard** is a developer CLI tool that analyzes Terraform plan JSON output and predicts the monthly Azure infrastructure cost impact prior to deployment.

---

## Features

- 🔍 **Terraform Plan Analysis**: Parses JSON representations of standard Terraform plans (`terraform show -json tfplan`).
- 💰 **Azure Infrastructure Pricing**: Queries Azure Retail Prices API to compute exact monthly cost deltas for created, deleted, or modified resources.
- ⚡ **Local SQLite Caching**: Caches Azure SKU pricing queries in `pricing_cache.db` for rapid local execution and offline usage.
- 🛡️ **Cost Guardrails**: Enforces maximum monthly cost increase thresholds with strict CI/CD exit status flags.
- 📊 **Rich Terminal Output**: Displays itemized resource tables and color-coded cost impact summaries directly in the terminal.

---

## Directory Structure

```
costguard/
├── costguard/
│   ├── __init__.py         # Package initialization & version info
│   ├── cli.py              # Command line argument parser & entry point
│   ├── parser.py           # Terraform plan JSON parser module
│   ├── pricing.py          # Azure Retail Prices API client
│   ├── cache.py            # SQLite database pricing cache manager
│   ├── calculator.py       # Cost impact calculator engine
│   ├── guardrail.py       # Cost guardrail & threshold policy engine
│   └── output.py           # Rich terminal table renderer
├── test-plans/
│   ├── plan_create.json    # Sample plan creating Azure VM & disk resources
│   ├── plan_delete.json    # Sample plan deleting legacy Azure resources
│   ├── plan_update.json    # Sample plan resizing/modifying Azure SKU sizes
│   └── plan_noise.json     # Sample plan containing non-cost & meta resources
├── tests/
│   ├── __init__.py
│   ├── test_cli.py         # Unit tests for CLI entry point
│   └── test_parser.py      # Unit tests for Terraform JSON parser
├── pricing_cache.db        # SQLite database file for local pricing cache
├── requirements.txt        # Python dependency specifications
├── setup.py                # Package setup script for CLI binary installation
├── README.md               # Overview and usage instructions
└── REPORT.md               # Architecture design report & development roadmap
```

---

## Installation

### Prerequisites
- Python 3.11 or higher
- SQLite3

### Install in Editable Mode
```bash
cd costguard
pip install -e .
```

Alternatively, install dependencies directly:
```bash
pip install -r requirements.txt
```

---

## CLI Usage

### View Help
```bash
costguard --help
```
or via Python module:
```bash
python -m costguard.cli --help
```

### Command Options

```
usage: costguard [-h] [-p FILE] [--currency CURRENCY] [--guardrail-limit AMOUNT] [--strict] [-v]

CostGuard: Predict monthly Azure infrastructure cost impacts from Terraform plan JSON files before deployment.

options:
  -h, --help            show this help message and exit
  -p FILE, --plan FILE  Path to Terraform plan JSON file (default: plan.json)
  --currency CURRENCY   Currency code for pricing calculation (default: USD)
  --guardrail-limit AMOUNT
                        Maximum acceptable monthly cost increase threshold
  --strict              Return non-zero exit status if guardrail limit is breached
  -v, --version         show program's version number and exit
```

---

## Quickstart Examples

### 1. Analyze Resource Creation
```bash
costguard --plan test-plans/plan_create.json
```

### 2. Analyze Resource Deletion
```bash
costguard --plan test-plans/plan_delete.json
```

### 3. Enforce Guardrail in CI/CD Pipelines
```bash
costguard --plan test-plans/plan_create.json --guardrail-limit 50 --strict
```
*(Returns exit code `1` if net monthly increase exceeds $50.00)*

---

## Running Tests

Run the test suite using pytest:
```bash
pytest tests/
```

---

## License

MIT License.
