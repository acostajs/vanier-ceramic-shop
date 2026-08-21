# User stories and Acceptance Criteria

Format: Gerkin - Given / When / Then

## Epic: Account Management

### US-01 - Register an account

- _As a_ visitor, _I want to_ create an account, _so that_ I can save my details and checkout faster in the future.
- Maps to: FR-ACC-01, FR-ACC-06, FR-ACC-07

**Acceptance Criteria:**

- _Given_ I am on the registration page, _when_ I submit valid email and matching password, _then_ my account is created and I am logged in / redirected appropriately.
- _Given_ I enter an email that is already registered, _when_ I submit, _then_ I see a clear "account already exists" error and no duplicate account is created.
- _Given_ I enter mismatched password fields, _when_ I submit, _then_ I see a validation error and the form is not submitted.

### US-02 - Log In

- _As a_ registered customer, _I want to_ log in, _so that_ I can access my account and order history.
- Maps to: FR-ACC-02, FR-ACC-03

**Acceptance Criteria:**

- _Given_ valid credentials, _when_ I submit the login form, _then_ I am authenticated and redirected to the intended page.
- _Given_ invalid credentials, _when_ I submit the login form, _then_ I see an error message and remain on the login page.

### US-03 Log Out

- _As a_ logged in customer, _I want to_ log out, _so that_ my account is secure on shared devices.
- Maps to: FR-ACC-04

**Acceptance Criteria:**

- _Given_ I am logged in, _when_ I click "log out", _then_ my session ends and I am redirected to a public page.

## Epic: Product Browsing

### US-04 - Browse product catalog

- _As a_ visitor, _I want to_ see a list of available ceramic products, _so that_ I can decide what to buy.
- Maps to: FR-SHOP-01

**Acceptance Criteria:**

- _Given_ I visit the shop page, _when_ the page loads, _then_ I see all active products with name, image, and price.

### US-05 - View product details

- _As a_ visitor, _I want to_ view a single product's details, _so that_ I can decide what to buy.
- Maps to: FR-SHOP-02, FR-SHOP-03

**Acceptance Criteria:**

- _Given_ a product exists, _when_ I click into it, _then_ I see its full description, price, image, and stock availability.
- _Given_ a product is out of stock, _when_ I view its page, _then_ the "Add to cart" action is disabled or hidden, and stock status is visibly indicated.

## Epic: Shopping Cart

### US-06 — Add item to cart

- _As a_ customer, _I want to_ add a product to my cart, _so that_ I can purchase it later.
- Maps to: FR-CART-01, FR-CART-06

**Acceptance Criteria:**

- _Given_ a product is in stock, _when_ I click "Add to Cart," _then_ the item appears in my cart with quantity 1 and the cart total updates.
- _Given_ I try to add more than available stock, _when_ I submit, _then_ I see an error and the cart is not updated beyond available stock.

### US-07 — Update cart quantity

- _As a_ customer, _I want to_ change the quantity of an item in my cart, _so that_ I can buy the right amount.
- Maps to: FR-CART-02, FR-CART-04

**Acceptance Criteria:**

- _Given_ an item is in my cart, _when_ I update its quantity, \_the_n the line total and cart total recalculate correctly.

### US-08 — Remove item from cart

- _As a_ customer, _I want to_ remove an item from my cart, _so that_ I only buy what I want.
- Maps to: FR-CART-03, FR-CART-04

**Acceptance Criteria:**

- _Given_ an item is in my cart, _when_ I remove it, _then_ it disappears from the cart and the total updates accordingly.

## Epic: Checkout & Payment

### US-09 — Complete checkout successfully

- _As a_ customer, _I want to_ pay for my cart via Stripe, _so that_ I can complete my purchase.
- Maps to: FR-PAY-01, FR-PAY-02, FR-PAY-04, FR-PAY-05

**Acceptance Criteria:**

- _Given_ items are in my cart, _when_ I proceed to checkout and complete payment with valid test card details, _then_ I am redirected to a confirmation page and an order is created with status "paid."
- _Given_ a webhook confirms payment, _when_ it is received, _then_ the order status updates without requiring the user to stay on the page.

### US-10 — Handle failed/cancelled payment

- _As a_ customer, _I want_ a cancelled or failed payment to not charge me or create a false order, _so that_ I'm not billed incorrectly.
- Maps to: FR-PAY-03

**Acceptance Criteria:**

- _Given_ I cancel checkout on the Stripe page, _when_ I return to the site, _then_ no order is created and my cart remains intact.

---

## Epic: Contact

### US-11 — Submit a contact inquiry

- _As a_ visitor, _I want to_ send a message to the shop, _so that_ I can ask questions before buying.
- Maps to: FR-CONT-01, FR-CONT-02, FR-CONT-03

**Acceptance Criteria:**

- _Given_ I fill in name, email, and message, _when_ I submit, _then_ I see a success confirmation.
- _Given_ I leave a required field blank, _when_ I submit, _then_ I see a validation error and the form is not submitted.
