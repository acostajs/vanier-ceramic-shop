import re
import random
import uuid
from locust import HttpUser, task, between


class CeramicShopUser(HttpUser):
    """Simulates real-world traffic by dynamically creating unique users

    and driving them through browsing, wishlisting, and checkout lifecycles.
    """

    wait_time = between(1.5, 5)

    def on_start(self) -> None:
        """Runs immediately when a virtual user is spawned."""
        self.product_urls = []
        self.csrf_token = ""

        # 1. Initialize clean, unique user identity state properties
        unique_id = uuid.uuid4().hex[:8]
        self.username = f"user_{unique_id}"
        self.email = f"{self.username}@example.com"
        self.password = "E2Epassword123!"

        # 2. Execute structured account lifecycle steps sequentially
        self.register_account()
        self.login_account()
        self.discover_products()

    def register_account(self) -> None:
        """Handles the complete step-by-step registration flow for a new user."""
        response = self.client.get("/en/account/registration/")
        csrf_token = self.extract_csrf(response.text)

        if not csrf_token:
            return

        payload = {
            "username": self.username,
            "first_name": "Perf",
            "last_name": "User",
            "email": self.email,
            "password1": self.password,
            "password2": self.password,
            "csrfmiddlewaretoken": response.cookies.get("csrftoken", csrf_token),
        }
        headers = {"Referer": f"{self.host}/en/account/registration/"}
        self.client.post(
            "/en/account/registration/submit/",
            data=payload,
            headers=headers,
            name="/account/registration/submit/",
        )

    def login_account(self) -> None:
        """Handles the separate authentication sequence for the created user session."""
        response = self.client.get("/en/account/login/")
        csrf_token = self.extract_csrf(response.text)

        if not csrf_token:
            return

        payload = {
            "username": self.username,
            "password": self.password,
            "csrfmiddlewaretoken": response.cookies.get("csrftoken", csrf_token),
        }
        headers = {"Referer": f"{self.host}/en/account/login/"}
        self.client.post(
            "/en/account/login/submit/",
            data=payload,
            headers=headers,
            name="/account/login/submit/",
        )

    def discover_products(self) -> None:
        """Scrapes the localized shop catalog view to collect active product item layers."""
        response = self.client.get("/en/shop/")
        if response.status_code == 200:
            found_urls = re.findall(
                r'href="((?:/en)?/shop/product/\d+/)"', response.text
            )
            if found_urls:
                self.product_urls = list(set(found_urls))

    def extract_csrf(self, html_text: str) -> str:
        """Helper utility using regex parsing to pull csrf token parameters out of layouts."""
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html_text)
        return match.group(1) if match else ""

    @task(4)
    def browse_catalog(self) -> None:
        """High frequency: Simulates general exploration of indexes and main covers."""
        self.client.get("/en/")
        self.client.get("/en/shop/")

    @task(3)
    def view_random_product(self) -> None:
        """Medium frequency: Clicking deeper into individual product details layers."""
        if self.product_urls:
            target_product = random.choice(self.product_urls)
            self.client.get(target_product, name="/en/shop/product/[id]/")

    @task(2)
    def interact_with_cart(self) -> None:
        """Lower frequency: Appending items to the cart and loading the cart review layout."""
        if self.product_urls:
            target_product = random.choice(self.product_urls)
            product_id = re.search(r"\d+", target_product).group()

            payload = {
                "quantity": 1,
                "csrfmiddlewaretoken": self.client.cookies.get("csrftoken", ""),
            }
            headers = {"Referer": f"{self.host}{target_product}"}

            self.client.post(
                f"/en/cart/add/{product_id}/",
                data=payload,
                headers=headers,
                name="/en/cart/add/[id]/",
            )
            self.client.get("/en/cart/", name="/en/cart/")

    @task(1)
    def interact_with_wishlist(self) -> None:
        """Lower frequency: Adding a product to the wishlist and viewing the account wishlist panel."""
        if self.product_urls:
            target_product = random.choice(self.product_urls)
            product_id = re.search(r"\d+", target_product).group()

            payload = {
                "csrfmiddlewaretoken": self.client.cookies.get("csrftoken", ""),
            }
            headers = {"Referer": f"{self.host}{target_product}"}

            # Post to the wishlist addition route
            self.client.post(
                f"/en/account/wishlist/add/{product_id}/",
                data=payload,
                headers=headers,
                name="/en/account/wishlist/add/[id]/",
            )
            # Navigate to look at the aggregated wishlist page layout
            self.client.get("/en/account/wishlist/", name="/en/account/wishlist/")

    @task(1)
    def complete_checkout_flow(self) -> None:
        """Lower frequency: Simulates loading the checkout overview page and

        triggering the Stripe Checkout Session initialization endpoint.
        """
        # 1. Access the checkout overview layout page to capture dynamic session cookies
        checkout_form_resp = self.client.get(
            "/en/cart/checkout/", name="/en/cart/checkout/"
        )

        # Guard clause to ensure the session contains cart items before checking out
        if "Your Cart is Empty" in checkout_form_resp.text:
            return

        csrf_token = self.extract_csrf(checkout_form_resp.text)

        # 2. Trigger your Stripe session generation endpoint
        payload = {
            "csrfmiddlewaretoken": self.client.cookies.get("csrftoken", csrf_token),
        }
        headers = {"Referer": f"{self.host}/en/cart/checkout/"}

        # This will simulate users clicking "Proceed to Payment"
        self.client.post(
            "/en/cart/checkout/stripe/",
            data=payload,
            headers=headers,
            name="/en/cart/checkout/stripe/",
        )
