def has_complete_addresses(account):
    """Return True if all billing & shipping fields are filled."""
    required_fields = [
        account.billing_address_line1,
        account.billing_city,
        account.billing_postal_code,
        account.billing_country,
        account.shipping_address_line1,
        account.shipping_city,
        account.shipping_postal_code,
        account.shipping_country,
    ]
    return all(required_fields)
