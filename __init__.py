"""Hermes plugin for the V3 product read-only API."""

from .schemas import GET_PRODUCT_DETAIL_SCHEMA, SEARCH_PRODUCTS_SCHEMA
from .tools import get_product_detail, search_products


def register(ctx):
    """Register V3 product tools with Hermes Agent."""
    ctx.register_tool(
        name="search_products",
        toolset="v3_product_api",
        schema=SEARCH_PRODUCTS_SCHEMA,
        handler=search_products,
    )
    ctx.register_tool(
        name="get_product_detail",
        toolset="v3_product_api",
        schema=GET_PRODUCT_DETAIL_SCHEMA,
        handler=get_product_detail,
    )

