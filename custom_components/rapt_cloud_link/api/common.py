from ..const import DEFAULT_API_BASE, DEV_API_BASE

def get_api_base(entry):
    """Return the correct API base depending on config entry options."""
    use_dev = entry.options.get("use_dev_api", False)
    return DEV_API_BASE if use_dev else DEFAULT_API_BASE

def get_token_url(entry):
    """Return the correct token URL depending on config entry options."""
    use_dev = entry.options.get("use_dev_api", False)
    return "https://dev.rapt.io/api/token" if use_dev else "https://api.rapt.io/api/token"