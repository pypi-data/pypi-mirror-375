"""
MCP server implementation for AKShare.
"""

import asyncio
import json
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from .api import (
    fetch_bond_zh_hs_cov_spot,
    fetch_forex_spot_quote,
    fetch_fund_etf_category_sina,
    fetch_fund_etf_hist_sina,
    fetch_futures_zh_spot,
    fetch_macro_china_cpi,
    fetch_macro_china_gdp,
    fetch_stock_zh_a_hist,
    fetch_stock_zh_a_spot,
    fetch_stock_zh_index_daily,
    fetch_stock_zh_index_spot,
    fetch_stock_zt_pool_strong_em,
)

# Configure logging
logger = logging.getLogger(__name__)


class AKShareTools(str, Enum):
    """
    Enum for AKShare tools.
    """
    STOCK_ZH_A_SPOT = "stock_zh_a_spot"
    STOCK_ZH_A_HIST = "stock_zh_a_hist"
    STOCK_ZH_INDEX_SPOT = "stock_zh_index_spot"
    STOCK_ZH_INDEX_DAILY = "stock_zh_index_daily"
    FUND_ETF_CATEGORY_SINA = "fund_etf_category_sina"
    FUND_ETF_HIST_SINA = "fund_etf_hist_sina"
    MACRO_CHINA_GDP = "macro_china_gdp"
    MACRO_CHINA_CPI = "macro_china_cpi"
    FOREX_SPOT_QUOTE = "forex_spot_quote"
    FUTURES_ZH_SPOT = "futures_zh_spot"
    BOND_ZH_HS_COV_SPOT = "bond_zh_hs_cov_spot"
    STOCK_ZT_POOL_STRONG_EM = "stock_zt_pool_strong_em"


# Create the server
server = Server("akshare")


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name=AKShareTools.STOCK_ZH_A_SPOT.value,
            description="获取中国A股市场股票实时数据",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name=AKShareTools.STOCK_ZH_A_HIST.value,
            description="获取中国A股市场股票历史数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "股票代码"},
                    "period": {"type": "string", "description": "数据频率：daily（日）、weekly（周）、monthly（月）"},
                    "start_date": {"type": "string", "description": "开始日期，格式为YYYYMMDD"},
                    "end_date": {"type": "string", "description": "结束日期，格式为YYYYMMDD"},
                    "adjust": {"type": "string", "description": "价格调整方式：''（不调整）、qfq（前复权）、hfq（后复权）"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AKShareTools.STOCK_ZH_INDEX_SPOT.value,
            description="获取中国股票市场指数实时数据",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name=AKShareTools.STOCK_ZH_INDEX_DAILY.value,
            description="获取中国股票市场指数每日数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "指数代码"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AKShareTools.FUND_ETF_CATEGORY_SINA.value,
            description="从新浪获取ETF基金数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "基金类别"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name=AKShareTools.FUND_ETF_HIST_SINA.value,
            description="从新浪获取ETF基金历史数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "ETF基金代码"},
                },
                "required": ["symbol"],
            },
        ),
        types.Tool(
            name=AKShareTools.MACRO_CHINA_GDP.value,
            description="获取中国GDP数据",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name=AKShareTools.MACRO_CHINA_CPI.value,
            description="获取中国CPI数据",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name=AKShareTools.FOREX_SPOT_QUOTE.value,
            description="获取外汇实时行情数据",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name=AKShareTools.FUTURES_ZH_SPOT.value,
            description="获取中国期货市场实时数据",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name=AKShareTools.BOND_ZH_HS_COV_SPOT.value,
            description="获取中国可转债实时数据",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name=AKShareTools.STOCK_ZT_POOL_STRONG_EM.value,
            description="从东方财富获取今日强势股票池数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "日期，格式为YYYYMMDD"},
                },
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any] | None
) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    try:
        if arguments is None:
            arguments = {}
            
        result = None
        
        match name:
            case AKShareTools.STOCK_ZH_A_SPOT.value:
                result = await fetch_stock_zh_a_spot()
            case AKShareTools.STOCK_ZH_A_HIST.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")
                
                period = arguments.get("period", "daily")
                start_date = arguments.get("start_date")
                end_date = arguments.get("end_date")
                adjust = arguments.get("adjust", "")
                
                result = await fetch_stock_zh_a_hist(
                    symbol=symbol,
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    adjust=adjust,
                )
            case AKShareTools.STOCK_ZH_INDEX_SPOT.value:
                result = await fetch_stock_zh_index_spot()
            case AKShareTools.STOCK_ZH_INDEX_DAILY.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")
                
                result = await fetch_stock_zh_index_daily(symbol=symbol)
            case AKShareTools.FUND_ETF_CATEGORY_SINA.value:
                category = arguments.get("category", "ETF基金")
                result = await fetch_fund_etf_category_sina(category=category)
            case AKShareTools.FUND_ETF_HIST_SINA.value:
                symbol = arguments.get("symbol")
                if not symbol:
                    raise ValueError("Missing required argument: symbol")
                
                result = await fetch_fund_etf_hist_sina(symbol=symbol)
            case AKShareTools.MACRO_CHINA_GDP.value:
                result = await fetch_macro_china_gdp()
            case AKShareTools.MACRO_CHINA_CPI.value:
                result = await fetch_macro_china_cpi()
            case AKShareTools.FOREX_SPOT_QUOTE.value:
                result = await fetch_forex_spot_quote()
            case AKShareTools.FUTURES_ZH_SPOT.value:
                result = await fetch_futures_zh_spot()
            case AKShareTools.BOND_ZH_HS_COV_SPOT.value:
                result = await fetch_bond_zh_hs_cov_spot()
            case AKShareTools.STOCK_ZT_POOL_STRONG_EM.value:
                date = arguments.get("date")
                result = await fetch_stock_zt_pool_strong_em(date=date)
            case _:
                raise ValueError(f"Unknown tool: {name}")
        
        # Convert result to JSON string with proper formatting
        result_json = json.dumps(result, ensure_ascii=False, indent=2)
        
        return [types.TextContent(type="text", text=result_json)]
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        error_message = f"Error executing tool {name}: {str(e)}"
        return [types.TextContent(type="text", text=error_message)]


async def main() -> None:
    """
    Main entry point for the server.
    """
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="akshare",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        ) 