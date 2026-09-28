"""Model-facing tool schemas for the V3 product API."""

SEARCH_PRODUCTS_SCHEMA = {
    "name": "search_products",
    "description": (
        "Search the V3 product catalog by product title, product number, "
        "SKU/configuration name, or barcode. Use this first when a user asks "
        "about a product and its product_id is not known."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "keyword": {
                "type": "string",
                "description": "Product name, product number, SKU name, or barcode.",
                "minLength": 1,
                "maxLength": 100,
            },
            "store_id": {
                "type": "integer",
                "description": "Optional store ID used to narrow the search.",
                "minimum": 1,
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of products to return.",
                "minimum": 1,
                "maximum": 20,
                "default": 10,
            },
        },
        "required": ["keyword"],
        "additionalProperties": False,
    },
}

GET_PRODUCT_DETAIL_SCHEMA = {
    "name": "get_product_detail",
    "description": (
        "Get one V3 product by product_id, including all returned product fields, "
        "SKU/configuration rows, inventory, prices, and product images. Use after "
        "search_products identifies the intended product."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "product_id": {
                "type": "integer",
                "description": "The V3 product ID returned by search_products.",
                "minimum": 1,
            }
        },
        "required": ["product_id"],
        "additionalProperties": False,
    },
}

