#!/usr/bin/env python3

import pytest

from french_tax_mcp.analyzers.income_analyzer import calculate_income_tax
from french_tax_mcp.scrapers.impots_scraper import get_tax_brackets


class TestIncomeTax:

    @pytest.mark.asyncio
    async def test_calculate_income_tax(self):
        result = await calculate_income_tax(50000, 2.0, 2024)
        
        assert result["status"] == "success"
        assert result["data"]["net_taxable_income"] == 50000
        assert result["data"]["household_parts"] == 2.0
        assert result["data"]["total_tax"] > 0

    @pytest.mark.asyncio
    async def test_get_tax_brackets(self):
        result = await get_tax_brackets(2024)
        
        assert result["status"] == "success"
        assert "brackets" in result["data"]
        assert len(result["data"]["brackets"]) > 0

    @pytest.mark.asyncio
    async def test_zero_income(self):
        result = await calculate_income_tax(0, 1.0, 2024)
        
        assert result["status"] == "success"
        assert result["data"]["total_tax"] == 0
