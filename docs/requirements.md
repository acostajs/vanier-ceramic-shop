# Requirements

## 1 Functional Requirements (FR)

### 1.1 Account Management (Module: Account)

| ID        | Requirement                                                                      |
| --------- | -------------------------------------------------------------------------------- |
| FR-ACC-01 | Users can register a new account with email and password.                        |
| FR-ACC-02 | Users can can log in with valid credentials.                                     |
| FR-ACC-03 | Users cannot log in with invalid credentials, and receive a clear error message. |
| FR-ACC-04 | Users can log out.                                                               |
| FR-ACC-05 | Users can view/edit their account/profile details.                               |
| FR-ACC-07 | Duplicate account registration (same email) is prevented with a clear error.     |
| FR-ACC-06 | password fields are marked and passwords are stored hashed, never in plaintext.  |

### 1.2 Product Catalog (Module: Shop)

| ID         | Requirement                                                                                   |
| ---------- | --------------------------------------------------------------------------------------------- |
| FR-SHOP-01 | User can view a list of available products.                                                   |
| FR-SHOP-02 | User can view a single product's detail page (name, price, description, image, stock status). |
| FR-SHOP-03 | Out of stock products are clearly indicated and cannot be added to the cart.                  |
| FR-SHOP-04 | Product listings can be filtered/searched.                                                    |

## 1.3 Shopping Cart (Module: Cart)

| ID         | Requirement                                                                  |
| ---------- | ---------------------------------------------------------------------------- |
| FR-CART-01 | Users can add a product to the cart from the product detail or listing page. |
| FR-CART-02 | User can update the quantity of an item in the cart.                         |
| FR-CART-03 | Users can remove an item from the cart.                                      |
| FR-CART-04 | Cart total updates correctly when items/quantities change.                   |
| FR-CART-05 | Cart persists for when the user is logged in.                                |
| FR-CART-06 | Adding a quantity greater than available stock is prevented or flagged.      |

### 1.4 Checkout and Payments (Module: Stripe)

| ID        | Requirement                                                       |
| --------- | ----------------------------------------------------------------- |
| FR-PAY-01 | Users can proceed from cart to Stripe Checkout.                   |
| FR-PAY-02 | A succesful payment creates an order record with status "paid".   |
| FR-PAY-03 | A failed/cancelled payment does not create a confirmed order.     |
| FR-PAY-04 | Stripe webhook events correctly update order status.              |
| FR-PAY-05 | Users receive on-screen confirmation after a successful checkout. |
| FR-PAY-06 | Duplicate webhook delivery does not duplicate orders.             |

### 1.5 Contact (Module: Contact)

| ID         | Requirement                                                    |
| ---------- | -------------------------------------------------------------- |
| FR-CONT-01 | Users can submit a contact form with name, email, and message. |
| FR-CONT-02 | Required fields are validated before submission.               |
| FR-CONT-03 | Users receive confirmation that their message was submitted.   |

## 2 Non-Functional Requirements

### 2.1 Performance

| ID          | Requirement                                                               |
| ----------- | ------------------------------------------------------------------------- |
| NFR-PERF-01 | Average server response time should remain under 200ms under normal load. |
| NFR-PERF-02 | 90th Percentile response time should remain under 300ms.                  |
| NFR-PERF-03 | Failure rate under load should remain at or near 0%.                      |

### 2.2 Security

| ID         | Requirement                                                                      |
| ---------- | -------------------------------------------------------------------------------- |
| NFR-SEC-01 | No card/payment data is stored or processed directly. This is managed by Stripe. |
| NFR-SEC-02 | Passwords are hashed.                                                            |
| NFR-SEC-03 | CSRF Protection is enabled on all forms.                                         |
| NFR-SEC-04 | Sessions cookies are secured appropriately for production.                       |
| NFR-SEC-05 | Environment secrets are not commited to source control.                          |

### 2.3 Usability

| ID         | Requirement                                                                                    |
| ---------- | ---------------------------------------------------------------------------------------------- |
| NFR-USE-01 | Core purchase flow (Browse -> Cart -> Checkout) can be completed without account registration. |
| NFR-USE-02 | Form validation erros are clear and displayed near the relevant field,                         |

### 2.4 Compatibility

| ID          | Requirement                                                          |
| ----------- | -------------------------------------------------------------------- |
| NFR-COMP-01 | Application renders correctly on latest Chrome, Firefox, and Safari. |
| NFR-COMP-02 | Application is usable on mobile widths down to 370px                 |

### 2.5 Reliability

| ID         | Requirement                                                                     |
| ---------- | ------------------------------------------------------------------------------- |
| NFR-REL-01 | Application maintains 100% test suite pass rate on main branch enforced via CI. |
| NFR-REL-02 | Database migrations apply cleanly on a fresh environment.                       |
