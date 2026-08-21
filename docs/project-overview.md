# Project Overview

## Project Name

Ceramic Shop

## Business Context

Ceramic shop is a direct-to-consumer online store for an artisanal ceramics business. It allows customers to browse a catalog of handmade ceramic products, create an account, manage a shopping cart, and complete purchases through Stripe.

While the application is fully functional as a store, the primary purpose of this project is to serve as a QA and Test Automation Showcase for my portfolio. To demostrate my approach as a tester to requirements analysis, test design, and automated test coverage on a production-style codebase.

## Goals of the Application

- Provide a simple, reliable online storefront for a small ceramics business.
- Support the full customer purchase journey from discovery -> Cart -> Account -> Checkout -> Payment confirmation.
- Demonstrate a secure handling of payment data via Stripe (no card data touches the app's own server)

## Primary Users

- **Guest / Customer:** Browses the catalog, can register an account, manages a cart, checks out.
- **Registered Customer:** Has an account, can log in, view order history, manage profile.
- **Admin:** Manages products. view orders via Django Admin.

## Key Features

- Product catalog browsing.
- Shopping cart management.
- Customer account registration and authentication.
- Checkout and payment processing via Stripe checkout and webhooks.
