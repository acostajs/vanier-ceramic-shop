# Data Requirements & Test Data Strategy

## Core Entities

| Entity             | Key Attributes                                                                  |
| ------------------ | ------------------------------------------------------------------------------- |
| **User**           | email, password (hashed), date joined                                           |
| **Product**        | name, description, price, stock quantity, image, active/inactive status         |
| **Cart**           | items (product + quantity), owner (session or user)                             |
| **Order**          | items, total, status (e.g., pending/paid/failed), Stripe session ID, timestamps |
| **ContactMessage** | name, email, message, submitted timestamp                                       |

## State Transitions (critical for test design)

**Order status lifecycle**:

```
[cart checkout initiated] → pending → paid → (fulfilled)
                                    → failed / cancelled
```

Each transition should have at least one test verifying the trigger (e.g., webhook event) and the resulting state.

**Product stock**:

```
in_stock → (quantity reaches 0) → out_of_stock
```

## Test Data Strategy by Test Level

| Test Level                 | Data Approach                                                                                                    |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Unit tests                 | Use factories/fixtures                                                                                           |
| Integration tests          | Use a dedicated test database (Django's test runner default); each test wrapped in a transaction that rolls back |
| API tests                  | Seed via API/ORM directly before assertions; avoid relying on data left over from other tests                    |
| E2E tests (Playwright)     | Requires a running app + test database; seed via management command or fixtures before test run                  |
| Performance tests (Locust) | Needs a realistic volume of product data to simulate genuine browsing/cart behavior                              |

## Test Data Principles

- **Isolation**: Tests must not depend on execution order or data left behind by other tests
- **Reproducibility**: Anyone running the suite from a fresh clone should get consistent results — no reliance on manually-seeded local data
- **No production data**: Test data is synthetic; the app should never test against real customer data
- **Stripe test mode only**: All payment tests use Stripe's test card numbers (e.g., `4242 4242 4242 4242`) and test API keys — this should be enforced (e.g., a check that fails loudly if live keys are detected in a test run)

## Seeding Approach

- Django management command (e.g., `manage.py seed_demo_data`)
- pytest fixtures/factories defined in `conftest.py`
- Django fixtures (JSON/YAML loaded via `loaddata`)

## Known Gaps / To Define

- Whether cart data is session-based (lost on logout) or persisted per user account
- Exact Order model status values and transition rules
- Whether webhook idempotency is handled via a unique Stripe event ID check
