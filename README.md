# Hermes V3 Product API Plugin

Adds two read-only tools to Hermes Agent:

- `search_products`: search by product title, product number, SKU name, or barcode.
- `get_product_detail`: retrieve product, SKU/configuration, inventory, price, and image data.

## Required configuration

Set these values when Hermes prompts during installation, or add them to
`~/.hermes/.env` on the Hermes server:

```env
V3_API_BASE_URL=https://v3.example.com
V3_API_TOKEN=replace-with-the-token-from-v3-api
```

`V3_API_BASE_URL` may be either the site root or the full `index.php` URL. For
example, both values below are accepted:

```text
https://v3.example.com
https://v3.example.com/index.php
```

Optional timeout configuration:

```env
V3_API_TIMEOUT_SECONDS=20
```

## Install

Push this directory to a Git repository. In the Hermes Dashboard, open
**Plugins**, paste the repository URL under **Install from GitHub / Git URL**,
select **Enable after install**, and click **Install**.

If this directory is stored inside another repository, append its path:

```text
owner/repository/hermes-v3-product-plugin
```

Restart the Hermes Gateway after installation or configuration changes.

## Test prompts

```text
Search for product ABC123.
```

```text
Find product ABC123, then tell me its available SKUs, prices, and stock.
```

## Security

The plugin sends `V3_API_TOKEN` only in the HTTP `Authorization: Bearer` header.
It never includes the token in tool output or logs. Use HTTPS for non-local API
connections.
