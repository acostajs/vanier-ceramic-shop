# Vanier Ceramic Shop - Test Suite Documentation

[![CI Status](https://github.com/acostajs/vanier-ceramic-shop/actions/workflows/deploy.yml/badge.svg)](https://github.com/acostajs/vanier-ceramic-shop/actions)
[![Coverage Status](https://img.shields.io/badge/Coverage-83%25-success)](file:///Users/juan/Documents/ceramic-shop/tests/docs/README.md)

This directory contains the automated test suite for the Laura Melissa Ceramic Shop. The suite covers everything from isolated model logic to end-to-end user flows and API integrations.

---

## Directory Structure

- **[tests/unit/](file:///Users/juan/Documents/ceramic-shop/tests/unit)**: Isolated unit tests for model fields, validation, and core cart logic.
- **[tests/integration/](file:///Users/juan/Documents/ceramic-shop/tests/integration)**: Database transactions, ORM query verification, and view status codes.
- **[tests/api/](file:///Users/juan/Documents/ceramic-shop/tests/api)**: Functional endpoint tests using `requests` and authentication tokens under a local live server.
- **[tests/e2e/](file:///Users/juan/Documents/ceramic-shop/tests/e2e)**: Playwright-driven end-to-end browser flows verifying user registration, catalog navigation, shopping cart updates, and mock Stripe Element views.
- **[tests/smoke/](file:///Users/juan/Documents/ceramic-shop/tests/smoke)**: Ultra-fast sanity-check Playwright E2E browser tests targeting all major storefront views to confirm page loading.

---

## Local Setup & Test Execution

### 1. Prerequisites
Ensure you have the Python environment set up with `uv` (the default package manager).

### 2. Install Dependencies
Run the following to synchronize your development and testing dependencies:
```bash
uv add -r requirements-test.txt
```

### 3. Install Playwright Browsers
Make sure the Playwright browser binaries are installed for end-to-end and smoke tests:
```bash
uv run playwright install
```

### 4. Run the Tests

- **Run all tests**:
  ```bash
  uv run pytest
  ```

- **Run tests with Coverage Report**:
  ```bash
  uv run pytest --cov=account --cov=cart --cov=contact --cov=shop --cov=main --cov-report=term-missing
  ```

- **Run only Smoke Tests**:
  ```bash
  uv run pytest tests/smoke/
  ```

- **Run only E2E Tests**:
  ```bash
  uv run pytest tests/e2e/
  ```

---

## Test Coverage Report

Current total test coverage is **83%**. Below is the module-by-module breakdown of the test coverage:

| Module        | Statements    | Misses    | Coverage % |
| :---          | :---          | :---      | :---       |
| **account**   | 213           | 46        | 78%        |
| **cart**      | 363           | 68        | 81%        |
| **contact**   | 56            | 0         | 100%       |
| **shop**      | 106           | 0         | 100%       |
| **main**      | 95            | 28        | 70%        |
| **TOTAL**     | **833**       | **142**   | **83%**    |
