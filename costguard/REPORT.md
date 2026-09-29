# CostGuard Architecture Design & Implementation Report

## Executive Summary

**CostGuard** is a lightweight, developer-first command-line tool built in Python 3.11+ that analyzes Terraform plan JSON files to predict monthly Azure infrastructure cost changes before code is applied or deployed. By evaluating planned infrastructure changes against Azure Retail Prices and enforcing cost guardrail thresholds, CostGuard empowers engineering teams to prevent cloud cost overruns directly in local development environments and CI/CD pipelines.

---

## 1. System Architecture

CostGuard follows a modular, single-responsibility architectural design pattern:

```
                          ┌────────────────────────┐
                          │   Terraform Plan JSON  │
                          └───────────┬────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │  costguard.parser      │
                          └───────────┬────────────┘
                                      │
                                      ▼
┌────────────────────────┐┌────────────────────────┐┌────────────────────────┐
│  costguard.pricing     ││  costguard.calculator  ││   costguard.cache      │
│  (Azure Retail API)    │◄┼──────────┬─────────────┼►│   (pricing_cache.db)   │
└────────────────────────┘└───────────┼────────────┘└────────────────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │  costguard.guardrail   │
                          └───────────┬────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │  costguard.output      │
                          │  (Rich Terminal UI)    │
                          └────────────────────────┘
```

### Key Modules:
- **`cli.py`**: Handles command-line arguments via `argparse`, orchestrates data flow across modules, and manages exit statuses.
- **`parser.py`**: Parses Terraform plan JSON schemas (v1.x standard format) and categorizes resource actions (`create`, `delete`, `update`, `no-op`).
- **`pricing.py`**: Interacts with Azure Retail Prices API via standard `requests` HTTP client to retrieve unauthenticated public prices.
- **`cache.py`**: Implements SQLite-backed persistent caching to store retrieved price records, eliminating redundant network calls and supporting offline analysis.
- **`calculator.py`**: Maps resource configuration attributes to monthly rates (using standard 730 hours/month cloud compute baselines) and calculates previous vs. proposed cost deltas.
- **`guardrail.py`**: Evaluates policy thresholds and determines CI/CD compliance.
- **`output.py`**: Formats and renders itemized resource impact tables and summary panels using `rich`.

---

## 2. Terraform Plan JSON Parsing Strategy

Terraform generates machine-readable plan JSON files via `terraform show -json tfplan`. CostGuard inspects the `resource_changes` array:

1. **Resource Identification**: Extracts `address`, `type`, `name`, and `provider_name`.
2. **Action Classification**: Evaluates `change.actions`:
   - `["create"]` -> Added Resource
   - `["delete"]` -> Deleted Resource
   - `["update"]` or `["create", "delete"]` -> Modified Resource
   - `["no-op"]` -> Unchanged Resource
3. **Attribute Extraction**: Inspects `change.before` and `change.after` dicts for key billing attributes (e.g., `size`, `disk_size_gb`, `storage_account_type`, `sku_name`).
4. **Noise Filtering**: Ignores meta/non-cost resources such as `random_string`, `null_resource`, or pure tag updates.

---

## 3. Azure Retail Prices API & Caching Strategy

### Azure Pricing API
CostGuard queries the public Azure Retail Prices REST API (`https://prices.azure.com/api/retail/prices`) using OData filters:
```
$filter = armSkuName eq '{sku}' and armRegionName eq '{region}' and priceType eq 'Consumption'
```
No API keys or Azure authentication are required, ensuring zero setup overhead for developers.

### SQLite Caching (`pricing_cache.db`)
To maximize execution speed and support offline environments:
- Table Schema: `pricing_cache(id, sku_name, region, currency, unit_price, unit_of_measure, updated_at)`
- Cache Hit: CostGuard checks SQLite first.
- Cache Miss: Fetches from Azure Retail Prices API and saves to SQLite.

---

## 4. Cost Guardrails & Pipeline Integration

CostGuard allows DevOps teams to define max cost increase thresholds via `--guardrail-limit <AMOUNT>`.

- **Standard Mode**: Displays pass/fail status banner in terminal without halting pipeline.
- **Strict Mode (`--strict`)**: Returns non-zero exit code (`1`) upon guardrail breach, making it suitable for blocking pull requests in GitHub Actions or Azure DevOps pipelines.

---

## 5. Development Phase Plan & Roadmap

### Phase 1: Foundation (Current Status)
- [x] Initial project structure setup.
- [x] `argparse` CLI implementation (`costguard --help`).
- [x] Baseline JSON parser, pricing API client, SQLite cache, calculator, and rich UI modules.
- [x] Creation of sample test plans (`plan_create.json`, `plan_delete.json`, `plan_update.json`, `plan_noise.json`).
- [x] Test suite with `pytest`.

### Phase 2: Expanded Resource Mapping
- [ ] Support expanded Azure resource coverage (AKS clusters, Cosmos DB, Azure SQL, Application Gateway, VPN Gateways).
- [ ] Add support for dynamic hourly-to-monthly multipliers based on region and usage patterns.
- [ ] Implement automatic TTL expiration logic for cached pricing data in SQLite.

### Phase 3: CI/CD & Developer Experience
- [ ] GitHub Action & Azure DevOps Pipeline templates.
- [ ] Automated PR comment generation with markdown cost impact tables.
- [ ] JSON export format flag (`--out-format json`) for automated downstream consumption.
