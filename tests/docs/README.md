# Test Suite Documentation

This folder contains the automated test suite for the **Vanier Ceramic Shop**.

The goal of this project is to show a complete testing strategy for a production-style Django application. The test suite covers everything from small unit tests to full browser automation and performance testing.

---

# Test Types

The project includes several types of automated tests.

| Folder               | Purpose                                                                                                                                                  |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/unit/`        | Tests for models, forms, views, and business logic.                                                                                                      |
| `tests/integration/` | Tests that verify different parts of the application work together, including database operations and Stripe webhooks.                                   |
| `tests/api/`         | Tests for API endpoints, authentication, requests, and responses.                                                                                        |
| `tests/e2e/`         | End-to-end browser tests using Playwright to simulate real user actions like registering, browsing products, adding items to the cart, and checking out. |
| `tests/smoke/`       | Fast browser tests that confirm the main pages load correctly.                                                                                           |
| `tests/performance/` | Load testing with Locust to measure application performance under traffic.                                                                               |

---

# Tools Used

* pytest
* Playwright
* Locust
* Coverage.py
* Ruff
* GitHub Actions

---

# Getting Started

## Requirements

* Python 3.13+
* Astral uv

Install the project dependencies:

```bash
uv sync
```

Install the Playwright browsers:

```bash
uv run playwright install
```

---

# Running Tests

Run the complete test suite:

```bash
uv run pytest
```

Run tests with a coverage report:

```bash
uv run task coverage
```

Generate an HTML coverage report:

```bash
uv run task coverage-report
```

Run only the smoke tests:

```bash
uv run pytest tests/smoke/
```

Run only the end-to-end tests:

```bash
uv run pytest tests/e2e/
```

---

# Test Coverage

The project currently has **100% test coverage** across every application module.

| Module    | Coverage |
| --------- | -------- |
| account   | 100%     |
| cart      | 100%     |
| contact   | 100%     |
| shop      | 100%     |
| **Total** | **100%** |

---

# Performance Testing

Performance testing is done with **Locust** to simulate multiple users browsing the store, managing carts, logging in, and completing a mock checkout.

Start the interactive Locust dashboard:

```bash
uv run task perf
```

Run the headless performance test:

```bash
uv run task perf-report
```

The included benchmark produced the following results:

| Metric                | Result     |
| --------------------- | ---------- |
| Average response time | **17 ms**  |
| Median response time  | **13 ms**  |
| 90th percentile       | **21 ms**  |
| Maximum response time | **118 ms** |
| Failure rate          | **0.00%**  |
| Total requests        | **39**     |

These results show that the application remains responsive and stable during the included load test.
