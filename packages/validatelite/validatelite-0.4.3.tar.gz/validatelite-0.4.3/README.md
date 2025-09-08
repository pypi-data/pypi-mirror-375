# ValidateLite

[![PyPI version](https://badge.fury.io/py/validatelite.svg)](https://badge.fury.io/py/validatelite)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Coverage](https://img.shields.io/badge/coverage-80%25-green.svg)](https://github.com/litedatum/validatelite)

**ValidateLite: A lightweight data validation tool for engineers who need answers, fast.**

Unlike other complex **data validation tools**, ValidateLite provides two powerful, focused commands for different scenarios:

*   **`vlite check`**: For quick, ad-hoc data checks. Need to verify if a column is unique or not null *right now*? The `check` command gets you an answer in 30 seconds, zero config required.

*   **`vlite schema`**: For robust, repeatable **database schema validation**. It's your best defense against **schema drift**. Embed it in your CI/CD and ETL pipelines to enforce data contracts, ensuring data integrity before it becomes a problem.

---

## Core Use Case: Automated Schema Validation

The `vlite schema` command is key to ensuring the stability of your data pipelines. It allows you to quickly verify that a database table or data file conforms to a defined structure.

### Scenario 1: Gate Deployments in CI/CD

Automatically check for breaking schema changes before they get deployed, preventing production issues caused by unexpected modifications.

**Example Workflow (`.github/workflows/ci.yml`)**
```yaml
jobs:
  validate-db-schema:
    name: Validate Database Schema
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install ValidateLite
        run: pip install validatelite

      - name: Run Schema Validation
        run: |
          vlite schema --conn "mysql://${{ secrets.DB_USER }}:${{ secrets.DB_PASS }}@${{ secrets.DB_HOST }}/sales" \
                           --rules ./schemas/customers_schema.json
```

### Scenario 2: Monitor ETL/ELT Pipelines

Set up validation checkpoints at various stages of your data pipelines to guarantee data quality and avoid "garbage in, garbage out."

**Example Rule File (`customers_schema.json`)**
```json
{
  "customers": {
    "rules": [
      { "field": "id", "type": "integer", "required": true },
      { "field": "name", "type": "string", "required": true },
      { "field": "email", "type": "string", "required": true },
      { "field": "age", "type": "integer", "min": 18, "max": 100 },
      { "field": "gender", "enum": ["Male", "Female", "Other"] },
      { "field": "invalid_col" }
    ]
  }
}
```

**Run Command:**
```bash
vlite schema --conn "mysql://user:pass@host:3306/sales" --rules customers_schema.json
```

### Advanced Schema Examples

**Multi-Table Validation:**
```json
{
  "customers": {
    "rules": [
      { "field": "id", "type": "integer", "required": true },
      { "field": "name", "type": "string", "required": true },
      { "field": "email", "type": "string", "required": true },
      { "field": "age", "type": "integer", "min": 18, "max": 100 }
    ],
    "strict_mode": true
  },
  "orders": {
    "rules": [
      { "field": "id", "type": "integer", "required": true },
      { "field": "customer_id", "type": "integer", "required": true },
      { "field": "total", "type": "float", "min": 0 },
      { "field": "status", "enum": ["pending", "completed", "cancelled"] }
    ]
  }
}
```

**CSV File Validation:**
```bash
# Validate CSV file structure
vlite schema --conn "sales_data.csv" --rules csv_schema.json --output json
```

**Complex Data Types:**
```json
{
  "events": {
    "rules": [
      { "field": "timestamp", "type": "datetime", "required": true },
      { "field": "event_type", "enum": ["login", "logout", "purchase"] },
      { "field": "user_id", "type": "string", "required": true },
      { "field": "metadata", "type": "string" }
    ],
    "case_insensitive": true
  }
}
```

**Available Data Types:**
- `string` - Text data (VARCHAR, TEXT, CHAR)
- `integer` - Whole numbers (INT, BIGINT, SMALLINT)
- `float` - Decimal numbers (FLOAT, DOUBLE, DECIMAL)
- `boolean` - True/false values (BOOLEAN, BOOL, BIT)
- `date` - Date only (DATE)
- `datetime` - Date and time (DATETIME, TIMESTAMP)

### Enhanced Schema Validation with Metadata

ValidateLite now supports **metadata validation** for precise schema enforcement without scanning table data. This provides superior performance by validating column constraints directly from database metadata.

**Metadata Validation Features:**
- **String Length Validation**: Validate `max_length` for string columns
- **Float Precision Validation**: Validate `precision` and `scale` for decimal columns
- **Database-Agnostic**: Works across MySQL, PostgreSQL, and SQLite
- **Performance Optimized**: Uses database catalog queries, not data scans

**Enhanced Schema Examples:**

**String Metadata Validation:**
```json
{
  "users": {
    "rules": [
      {
        "field": "username",
        "type": "string",
        "max_length": 50,
        "required": true
      },
      {
        "field": "email",
        "type": "string",
        "max_length": 255,
        "required": true
      },
      {
        "field": "biography",
        "type": "string",
        "max_length": 1000
      }
    ]
  }
}
```

**Float Precision Validation:**
```json
{
  "products": {
    "rules": [
      {
        "field": "price",
        "type": "float",
        "precision": 10,
        "scale": 2,
        "required": true
      },
      {
        "field": "weight",
        "type": "float",
        "precision": 8,
        "scale": 3
      }
    ]
  }
}
```

**Mixed Metadata Schema:**
```json
{
  "orders": {
    "rules": [
      { "field": "id", "type": "integer", "required": true },
      {
        "field": "customer_name",
        "type": "string",
        "max_length": 100,
        "required": true
      },
      {
        "field": "total_amount",
        "type": "float",
        "precision": 12,
        "scale": 2,
        "required": true
      },
      { "field": "order_date", "type": "datetime", "required": true },
      { "field": "notes", "type": "string", "max_length": 500 }
    ],
    "strict_mode": true
  }
}
```

**Backward Compatibility**: Existing schema files without metadata continue to work unchanged. Metadata validation is optional and can be added incrementally to enhance validation precision.

**Command Options:**
```bash
# Basic validation
vlite schema --conn <connection> --rules <rules_file>

# JSON output for automation
vlite schema --conn <connection> --rules <rules_file> --output json

# Exit with error code on any failure
vlite schema --conn <connection> --rules <rules_file> --fail-on-error

# Verbose logging
vlite schema --conn <connection> --rules <rules_file> --verbose
```

---

## Quick Start: Ad-Hoc Checks with `check`

For temporary, one-off validation needs, the `check` command is your best friend.

**1. Install (if you haven't already):**
```bash
pip install validatelite
```

**2. Run a check:**
```bash
# Check for nulls in a CSV file's 'id' column
vlite check --conn "customers.csv" --table customers --rule "not_null(id)"

# Check for uniqueness in a database table's 'email' column
vlite check --conn "mysql://user:pass@host/db" --table customers --rule "unique(email)"
```

---

## Learn More

- **[Usage Guide (USAGE.md)](docs/USAGE.md)**: Learn about all commands, arguments, and advanced features.
- **[Configuration Reference (CONFIG_REFERENCE.md)](docs/CONFIG_REFERENCE.md)**: See how to configure the tool via `toml` files.
- **[Contributing Guide (CONTRIBUTING.md)](CONTRIBUTING.md)**: We welcome contributions!

---

## 📝 Development Blog

Follow the journey of building ValidateLite through our development blog posts:

- **[DevLog #1: Building a Zero-Config Data Validation Tool](https://blog.litedatum.com/posts/Devlog01-data-validation-tool/)**
- **[DevLog #2: Why I Scrapped My Half-Built Data Validation Platform](https://blog.litedatum.com/posts/Devlog02-Rethinking-My-Data-Validation-Tool/)
- **[Rule-Driven Schema Validation: A Lightweight Solution](https://blog.litedatum.com/posts/Rule-Driven-Schema-Validation/)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
