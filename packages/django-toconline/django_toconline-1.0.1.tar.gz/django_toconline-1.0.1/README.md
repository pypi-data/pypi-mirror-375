# Django TOC Online

Lightweight, reusable Django integration for the TOC Online API (Portugal). This package provides:

- OAuth2 token persistence via a simple `TocOnlineToken` model.
- A small client wrapper (`TocOnline`) around the TOC Online HTTP API for common operations (list, retrieve, create, update, delete, download, send, cancel).
- Constants for known API resources and document kinds in `toconline.resources`.

Official API documentation: [TOC Online API Docs](https://api-docs.toconline.pt/) (OpenAPI/Swagger + Postman collection available).

## Motive and design

This package was written with simplicity and resilience in mind. The goal is not to provide a full-blown, object-oriented SDK that models every TOC Online resource (eg: no `Product`, `Client`, `Document` classes). Instead:

- Keep the wrapper super-generic and minimal. The client forwards requests to the TOC Online API and returns the API response data as-is (with one small convenience: the outer `data` JSON envelope is removed so you get the underlying data directly).
- Avoid strong coupling to the exact shape of resource objects. By not creating per-resource classes, the package is more resilient to future changes in the API's object models.
- Focus on the two most useful conveniences: managing the OAuth2 authentication flow (token acquisition and refresh) and making it easy to download printable documents (PDFs) from the service.

This design favors durability and small surface area over rich client-side models.

## Quick checklist

- [x] Inspect repository code to identify usage and configuration points
- [x] Reviewed public API docs at [TOC Online API Docs](https://api-docs.toconline.pt/)
- [x] Wrote this README covering install, config, usage, testing and links

## Installation

Install from PyPI (when published) or install in editable mode for development:

```bash
pip install django-toconline
```

Add `toconline` to your Django `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'toconline',
]
```

## Configuration

The package expects a few Django settings (or environment variables mapped into settings) to be present:

- TOCONLINE_BASE_URL: Base URL for the TOC Online API (example: `https://app10.toconline.pt`)
- TOCONLINE_OAUTH_CLIENT_ID: OAuth client id
- TOCONLINE_OAUTH_CLIENT_SECRET: OAuth client secret
- TOCONLINE_OAUTH_REDIRECT_URI: Redirect URI used for the OAuth flow
- TOCONLINE_TIMEOUT: (optional) HTTP request timeout in seconds (default: 10 seconds)

Example (Django settings from environment variables):

```python
TOCONLINE_BASE_URL = os.getenv('TOCONLINE_BASE_URL')  # https://app<N>.toconline.pt
TOCONLINE_OAUTH_CLIENT_ID = os.getenv('TOCONLINE_OAUTH_CLIENT_ID')
TOCONLINE_OAUTH_CLIENT_SECRET = os.getenv('TOCONLINE_OAUTH_CLIENT_SECRET')
TOCONLINE_OAUTH_REDIRECT_URI = os.getenv('TOCONLINE_OAUTH_REDIRECT_URI')
TOCONLINE_TIMEOUT = int(os.getenv('TOCONLINE_TIMEOUT', 10))  # optional.
```

The tests in the repository's `tests/` directory provide usage examples for contributors and are not included in the packaged distribution.

If you plan to contribute with more tests, run them locally with:

```bash
make test
```

## Usage

The package exposes a `toconline` client instance configured from Django settings in `toconline.services`.

*Authentication is automatic:* the client will acquire an access token on-demand and refresh it proactively when needed — you do not need to call `authenticate()` or `refresh()` manually. Just call the CRUD methods (for example `list`, `create`, `update`) and the client handles authentication for you.

Simple examples:

```python
from toconline.resources import TocOnlineResource, TocOnlineDocumentKind
from toconline import services

# List customers (returns the API response data)
customers = services.toconline.list(
    TocOnlineResource.CUSTOMERS,
    limit=10
)

# Get first product matching a filter
product = services.toconline.first(
    TocOnlineResource.PRODUCTS,
    sales_price=100
)

# Create a resource (attributes depend on the resource)
new_customer = services.toconline.create(
    TocOnlineResource.CUSTOMERS,
    business_name='Acme, Lda',
    contact_name='John Doe',
    tax_registration_number='999999990',
    ...
)

# Retrieve, update and delete
item = services.toconline.retrieve(
    TocOnlineResource.PRODUCTS,
    '123'
)

services.toconline.update(
    TocOnlineResource.PRODUCTS,
    '123',
    contact_name='Jane Doe',
    ...
)

services.toconline.delete(
    TocOnlineResource.PRODUCTS,
    '123'
)

# Download a printable document (PDF bytes)
pdf_bytes = services.toconline.download_document(
    'document-id',
    kind=TocOnlineDocumentKind.DOCUMENT,
    n_copies=3
)

with open('doc.pdf', 'wb') as fh:
    fh.write(pdf_bytes)
```

See `toconline.services.TocOnline` for full client methods and behavior. The client handles token acquisition and refresh via the `TocOnlineToken` model in `toconline.models`.

### Forward-compatibility / generic endpoints

The client implements generic CRUD helpers that build requests from the resource path you pass. In practice this means the library routes calls to `/api/{resource}` and does not require a dedicated client class for each new resource the TOC Online API may add later. Because the helpers are path-driven, you can call a resource string directly even if `TocOnlineResource` hasn't been updated in this package yet.

- `TocOnlineResource` is a convenience; you may continue to use it, but plain resource strings work the same.
- The client forwards requests and returns the API response data largely unchanged (the outer `data` envelope is removed). Always follow the official API schema for request attributes.

Examples:

```python
# Using the enum (recommended when available)
services.toconline.create(TocOnlineResource.CUSTOMERS, business_name='Acme, Lda')

# Using a resource string that the package doesn't (yet) list
# This will POST to /api/new-resource
services.toconline.create('new-resource', attr1='abc', attr2=123)

# Update / retrieve still work the same: resource path + id
services.toconline.update('new-resource', 'resource-id', name='updated')
services.toconline.retrieve('new-resource', 'resource-id')
```

Notes:

- Forward-compatibility means you can call new endpoints immediately, but the accepted payload and returned schema are defined by the TOC Online API — consult the official docs for details.
- Because the client returns API data directly, consumer code should handle new fields or schema changes gracefully.

## API Resources

The most-used API resources are listed in `toconline.resources.TocOnlineResource`. The client offers generic CRUD helpers for:

- Core entities: customers, suppliers, addresses, contacts
- Catalog items: products, services
- Financial documents: commercial sales documents and receipts, commercial purchase documents and payments
- Auxiliary resources: tax descriptors, item families, countries, units of measure, bank and cash accounts, currencies, taxes, expense categories and commercial document series

Beyond CRUD, the client exposes document-specific operations (subject to the API rules — see the official docs): downloading printable output (PDF bytes), canceling/voiding documents, sending documents via email, and communicating documents to the tax authority (AT).

For a full list and request/response schemas consult the official docs: [TOC Online API Docs](https://api-docs.toconline.pt/) and the OpenAPI/Swagger link provided there.

## Authentication and tokens

- Tokens are persisted in the `TocOnlineToken` model (`toconline.models.TocOnlineToken`).
- The client proactively refreshes tokens when they are near expiry.
- The token model exposes convenience properties like `expires_at`, `is_expiring_soon` and `is_expired`. Note that `is_expiring_soon` and `is_expired` use a small safety skew to trigger proactive refreshes.

Authentication is seamless: on the first API call the client will obtain an access token automatically and persist it. If a token is near expiry the client will refresh it before making requests so your code does not need to manage the OAuth flow explicitly. Example:

```python
from toconline.resources import TocOnlineResource
from toconline.services import toconline

# No explicit authenticate/refresh calls needed - the client does this for you!
# In other words, no need for something like toconline.authenticate() or toconline.refresh()
customers = toconline.list(TocOnlineResource.CUSTOMERS)
```

## Tests

Project tests live under `tests/`. The test settings use an in-memory SQLite database and include example default TOCONLINE_* settings.

Run the test suite (project includes a Makefile target `test`):

```bash
make test
```

## Development notes

- The client is intentionally thin — it mirrors the TOC Online API endpoints and uses `requests` under the hood.
- The public API docs (OpenAPI/Swagger and Postman) are the authoritative source for field names, allowed values and example payloads. Use them when composing create/update payloads.

Official docs: [TOC Online API Docs](https://api-docs.toconline.pt/) (includes a Swagger/OpenAPI viewer and a Postman collection)

## Contributing

Contributions welcome. Please open issues and pull requests. Keep changes small and include tests for new behavior.

## License

This project is licensed under the MIT License (see `LICENSE`).

## Support / Buy me a coffee

If you find this project helpful, you can support its development via Buy Me a Coffee. Add your own link or replace the placeholder below:

[Buy me a coffee](https://buymeacoffee.com/dmp593)
