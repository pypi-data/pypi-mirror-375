# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""French Tax MCP server implementation.

This server provides tools for French tax calculations and information retrieval.
"""

import argparse
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

# Removed business_analyzer import - keeping only individual income tax
from french_tax_mcp.analyzers.income_analyzer import calculate_income_tax
# Removed property_analyzer import - keeping only individual income tax
from french_tax_mcp.report_generator import generate_tax_report
# Import scrapers lazily to avoid initialization delays
# from french_tax_mcp.scrapers.impots_scraper import get_form_info, get_tax_brackets
# from french_tax_mcp.scrapers.legal_scraper import get_tax_article, search_tax_law
# from french_tax_mcp.scrapers.service_public_scraper import (
#     get_tax_deadlines,
#     get_tax_procedure,
# )

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="french-tax-mcp",
    instructions="""Use this server for retrieving French tax information, with a focus on individual taxpayers.

    REQUIRED WORKFLOW:
    Retrieve tax information by following these steps in order:

    1. Primary Data Source:
       - MUST first invoke get_tax_info_from_web() to scrape information from official websites

    2. Fallback Mechanism:
       - If web scraping fails, MUST use get_cached_tax_info() to fetch previously cached data

    3. For Individual Income Tax Information:
       - Use get_tax_brackets() for current tax brackets
       - Use calculate_income_tax() for tax calculations

    4. Report Generation:
       - MUST generate tax information report using retrieved data via generate_tax_report()
       - The report includes sections for:
         * Overview of the tax scheme/rule
         * Eligibility criteria
         * Calculation methods
         * Important deadlines
         * Recent changes
         * Practical examples

    ACCURACY GUIDELINES:
    - When uncertain about tax rules or calculations, EXCLUDE them rather than making assumptions
    - Always cite the specific article of the tax code or official source
    - PROVIDING LESS INFORMATION IS BETTER THAN GIVING WRONG INFORMATION
    - Always include the effective date of the tax information
    """,
    dependencies=["pydantic", "beautifulsoup4", "httpx"],
)


class TaxInfoRequest(BaseModel):
    """Request model for tax information queries."""

    topic: str = Field(..., description="The tax topic to search for (e.g., 'tranches_impot', 'pinel', 'lmnp')")
    year: Optional[int] = Field(None, description="Tax year (defaults to current year if not specified)")


@mcp.tool(
    name="get_tax_info_from_web",
    description="Get tax information from official French government websites like impots.gouv.fr, service-public.fr, or legifrance.gouv.fr",
)
async def get_tax_info_from_web(tax_topic: str, ctx: Context, year: Optional[int] = None) -> Optional[Dict]:
    """Get tax information from official French government websites.

    Args:
        tax_topic: The tax topic to search for (e.g., 'tranches_impot', 'pinel', 'lmnp')
        year: Optional tax year (defaults to current year if not specified)
        ctx: MCP context for logging and state management

    Returns:
        Dict: Dictionary containing the tax information retrieved from the website
    """
    try:
        # This is a placeholder implementation
        # The actual implementation will be more complex and will use specialized scrapers

        # Set default year to current year if not specified
        if year is None:
            year = datetime.now().year

        await ctx.info(f"Retrieving information about {tax_topic} for year {year}")

        # Map topic to appropriate scraper
        if tax_topic.lower() in ["tranches_impot", "baremes", "tax_brackets"]:
            # Use tax brackets scraper (lazy import)
            from french_tax_mcp.scrapers.impots_scraper import get_tax_brackets
            result = await get_tax_brackets(year)
            return result
        else:
            # Generic response for now
            return {
                "status": "error",
                "message": f"Information for {tax_topic} not yet implemented",
                "year": year,
            }

    except Exception as e:
        await ctx.error(f"Failed to get tax information from web: {e}")
        return {
            "status": "error",
            "message": f"Error retrieving information: {str(e)}",
            "topic": tax_topic,
            "year": year,
        }


@mcp.tool(
    name="get_tax_brackets",
    description="Get income tax brackets (tranches d'imposition) for a specific year",
)
async def get_tax_brackets_wrapper(ctx: Context, year: Optional[int] = None) -> Optional[Dict]:
    """Get income tax brackets for a specific year.

    Args:
        year: Tax year (defaults to current year if not specified)
        ctx: MCP context for logging and state management

    Returns:
        Dict: Dictionary containing the tax brackets and rates
    """
    try:
        # Set default year to current year if not specified
        if year is None:
            year = datetime.now().year

        await ctx.info(f"Retrieving tax brackets for year {year}")

        # Call the implementation from impots_scraper.py (lazy import)
        from french_tax_mcp.scrapers.impots_scraper import get_tax_brackets
        result = await get_tax_brackets(year)
        return result
    except Exception as e:
        await ctx.error(f"Failed to get tax brackets: {e}")
        return {
            "status": "error",
            "message": f"Error retrieving tax brackets: {str(e)}",
            "year": year,
        }



@mcp.tool(
    name="get_form_details",
    description="Get detailed information about a specific tax form including fields and instructions",
)
async def get_form_details_wrapper(form_number: str, ctx: Context, year: Optional[int] = None) -> Optional[Dict]:
    """Get detailed information about a specific tax form.

    Args:
        form_number: The form number (e.g., '2042', '2044', '2072')
        year: Tax year (defaults to current year if not specified)
        ctx: MCP context for logging and state management

    Returns:
        Dict: Dictionary containing detailed information about the tax form
    """
    try:
        # Set default year to current year if not specified
        if year is None:
            year = datetime.now().year

        await ctx.info(f"Retrieving details for form {form_number} for year {year}")

        # Try to get information from the scraper first
        try:
            from french_tax_mcp.scrapers.impots_scraper import get_form_info
            result = await get_form_info(form_number, year)
            if result.get("status") == "success":
                return result
        except Exception as e:
            await ctx.warning(f"Failed to get form details from web: {e}. Using fallback data.")

        # If web scraping fails or returns an error, use fallback data
        form_number = form_number.strip()

        # Provide fallback data for common forms
        if form_number == "2042":
            return {
                "status": "success",
                "message": f"Retrieved fallback information for form 2042 for {year}",
                "data": {
                    "form": "2042",
                    "year": year,
                    "title": "Déclaration des revenus",
                    "description": "Formulaire principal de déclaration des revenus des personnes physiques.",
                    "sections": [
                        "État civil et situation de famille",
                        "Traitements, salaires, pensions et rentes",
                        "Revenus de capitaux mobiliers",
                        "Plus-values et gains divers",
                        "Revenus fonciers",
                        "Charges déductibles",
                        "Réductions et crédits d'impôt",
                    ],
                    "deadline": f"31 mai {year} (déclaration en ligne)",
                    "related_forms": [
                        {"number": "2042-C", "title": "Déclaration complémentaire"},
                        {"number": "2042-RICI", "title": "Réductions d'impôt et crédits d'impôt"},
                        {"number": "2044", "title": "Revenus fonciers"},
                    ],
                    "download_link": "https://www.impots.gouv.fr/formulaire/2042/declaration-des-revenus",
                },
                "source": "Fallback data",
            }
        elif form_number == "2044":
            return {
                "status": "success",
                "message": f"Retrieved fallback information for form 2044 for {year}",
                "data": {
                    "form": "2044",
                    "year": year,
                    "title": "Déclaration des revenus fonciers",
                    "description": "Formulaire de déclaration des revenus fonciers (locations non meublées).",
                    "sections": [
                        "Propriétés rurales et urbaines",
                        "Recettes brutes",
                        "Frais et charges",
                        "Intérêts d'emprunt",
                        "Détermination du revenu ou déficit",
                    ],
                    "deadline": f"31 mai {year} (avec la déclaration principale)",
                    "related_forms": [
                        {"number": "2042", "title": "Déclaration des revenus"},
                        {
                            "number": "2044-SPE",
                            "title": "Déclaration des revenus fonciers spéciaux",
                        },
                    ],
                    "download_link": "https://www.impots.gouv.fr/formulaire/2044/declaration-des-revenus-fonciers",
                },
                "source": "Fallback data",
            }
        elif form_number == "2031":
            return {
                "status": "success",
                "message": f"Retrieved fallback information for form 2031 for {year}",
                "data": {
                    "form": "2031",
                    "year": year,
                    "title": "Déclaration des résultats BIC",
                    "description": "Formulaire de déclaration des bénéfices industriels et commerciaux (BIC) au régime réel.",
                    "sections": [
                        "Identification de l'entreprise",
                        "Résultat fiscal",
                        "Immobilisations et amortissements",
                        "Provisions",
                        "Plus-values et moins-values",
                    ],
                    "deadline": f"Début mai {year} (entreprises soumises à l'IR)",
                    "related_forms": [
                        {"number": "2033-A à G", "title": "Régime simplifié"},
                        {"number": "2042-C-PRO", "title": "Report des revenus professionnels"},
                    ],
                    "download_link": "https://www.impots.gouv.fr/formulaire/2031-sd/declaration-de-resultats",
                },
                "source": "Fallback data",
            }
        else:
            # For unknown forms, return a more informative error
            return {
                "status": "error",
                "message": f"Information for form {form_number} not available",
                "form": form_number,
                "year": year,
                "available_forms": ["2042", "2044", "2031"],
            }
    except Exception as e:
        await ctx.error(f"Failed to get form details: {e}")
        return {
            "status": "error",
            "message": f"Error retrieving form details: {str(e)}",
            "form": form_number,
            "year": year,
        }


@mcp.tool(
    name="get_cached_tax_info",
    description="Get cached tax information when web scraping fails",
)
async def get_cached_tax_info(tax_topic: str, ctx: Context, year: Optional[int] = None) -> Optional[Dict]:
    """Get cached tax information when web scraping fails.

    Args:
        tax_topic: The tax topic to search for (e.g., 'tranches_impot', 'pinel', 'lmnp')
        year: Optional tax year (defaults to current year if not specified)
        ctx: MCP context for logging and state management

    Returns:
        Dict: Dictionary containing the cached tax information
    """
    try:
        # Set default year to current year if not specified
        if year is None:
            year = datetime.now().year

        await ctx.info(f"Retrieving cached information for {tax_topic} for year {year}")

        # Map topic to appropriate cached data
        if tax_topic.lower() in ["tranches_impot", "baremes", "tax_brackets"]:
            # Use tax brackets fallback data (lazy import)
            from french_tax_mcp.scrapers.impots_scraper import ImpotsScraper

            scraper = ImpotsScraper()
            brackets = scraper._get_fallback_brackets(year)

            return {
                "status": "success",
                "message": f"Retrieved cached tax brackets for {year}",
                "data": {
                    "year": year,
                    "brackets": brackets,
                },
                "source": "cache",
            }
        else:
            # Generic response for now
            return {
                "status": "error",
                "message": f"Cached information for {tax_topic} not yet implemented",
                "topic": tax_topic,
                "year": year,
                "source": "cache",
            }

    except Exception as e:
        await ctx.error(f"Failed to get cached tax information: {e}")
        return {
            "status": "error",
            "message": f"Error retrieving cached information: {str(e)}",
            "topic": tax_topic,
            "year": year,
        }


@mcp.tool(
    name="calculate_income_tax",
    description="Calculate French income tax based on net taxable income and household composition",
)
async def calculate_income_tax_wrapper(
    net_taxable_income: float,
    household_parts: float = 1.0,
    year: Optional[int] = None,
    ctx: Optional[Context] = None,
) -> Optional[Dict]:
    """Calculate income tax based on net taxable income and household composition.

    Args:
        net_taxable_income: Net taxable income in euros
        household_parts: Number of household parts (quotient familial)
        year: Tax year (defaults to current year)
        ctx: MCP context for logging

    Returns:
        Dict: Dictionary containing tax calculation details
    """
    try:
        if ctx:
            await ctx.info(f"Calculating income tax for {net_taxable_income}€ with {household_parts} parts")

        result = await calculate_income_tax(net_taxable_income, household_parts, year)
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to calculate income tax: {e}")
        return {
            "status": "error",
            "message": f"Error calculating income tax: {str(e)}",
        }


        return {
            "status": "error",
            "message": f"Error calculating LMNP benefit: {str(e)}",
        }


@mcp.tool(
    name="get_tax_procedure",
    description="Get information about a tax procedure from service-public.fr",
)
async def get_tax_procedure_wrapper(
    procedure_name: str,
    ctx: Optional[Context] = None,
) -> Optional[Dict]:
    """Get information about a tax procedure from service-public.fr.

    Args:
        procedure_name: Name of the procedure (e.g., 'declaration_revenus', 'credit_impot')
        ctx: MCP context for logging

    Returns:
        Dict: Dictionary containing procedure information
    """
    try:
        if ctx:
            await ctx.info(f"Getting tax procedure information for {procedure_name}")

        from french_tax_mcp.scrapers.service_public_scraper import get_tax_procedure
        result = await get_tax_procedure(procedure_name)
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to get tax procedure: {e}")
        return {
            "status": "error",
            "message": f"Error getting tax procedure: {str(e)}",
        }


@mcp.tool(
    name="get_tax_deadlines",
    description="Get tax deadlines from service-public.fr",
)
async def get_tax_deadlines_wrapper(
    year: Optional[int] = None,
    ctx: Optional[Context] = None,
) -> Optional[Dict]:
    """Get tax deadlines from service-public.fr.

    Args:
        year: The tax year to retrieve deadlines for (defaults to current year)
        ctx: MCP context for logging

    Returns:
        Dict: Dictionary containing tax deadlines
    """
    try:
        if ctx:
            await ctx.info(f"Getting tax deadlines for year {year or 'current'}")

        from french_tax_mcp.scrapers.service_public_scraper import get_tax_deadlines
        result = await get_tax_deadlines(year)
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to get tax deadlines: {e}")
        return {
            "status": "error",
            "message": f"Error getting tax deadlines: {str(e)}",
        }


@mcp.tool(
    name="health_check",
    description="Simple health check to verify the server is responsive",
)
async def health_check(ctx: Optional[Context] = None) -> Dict:
    """Simple health check to verify the server is responsive.
    
    Returns:
        Dict: Status information about the server
    """
    if ctx:
        await ctx.info("Health check requested")
    
    return {
        "status": "success",
        "message": "French Tax MCP Server is running",
        "timestamp": datetime.now().isoformat(),
        "available_tools": [
            "calculate_income_tax",
            "get_tax_brackets", 
            "get_scheme_details",
            "calculate_pinel_benefit",
            "calculate_lmnp_benefit"
        ]
    }


@mcp.tool(
    name="get_tax_article",
    description="Get information about a tax law article from legifrance.gouv.fr",
)
async def get_tax_article_wrapper(
    article_id: str,
    ctx: Optional[Context] = None,
) -> Optional[Dict]:
    """Get information about a tax law article from legifrance.gouv.fr.

    Args:
        article_id: Article identifier (e.g., '200', '4B')
        ctx: MCP context for logging

    Returns:
        Dict: Dictionary containing article information
    """
    try:
        if ctx:
            await ctx.info(f"Getting tax article information for {article_id}")

        result = await get_tax_article(article_id)
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to get tax article: {e}")
        return {
            "status": "error",
            "message": f"Error getting tax article: {str(e)}",
        }


@mcp.tool(
    name="search_tax_law",
    description="Search for tax law articles on legifrance.gouv.fr",
)
async def search_tax_law_wrapper(
    query: str,
    ctx: Optional[Context] = None,
) -> Optional[Dict]:
    """Search for tax law articles on legifrance.gouv.fr.

    Args:
        query: Search query
        ctx: MCP context for logging

    Returns:
        Dict: Dictionary containing search results
    """
    try:
        if ctx:
            await ctx.info(f"Searching tax law for: {query}")

        result = await search_tax_law(query)
        return result
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to search tax law: {e}")
        return {
            "status": "error",
            "message": f"Error searching tax law: {str(e)}",
        }


@mcp.tool(
    name="generate_tax_report",
    description="Generate a detailed report about a specific tax topic",
)
async def generate_tax_report_wrapper(
    tax_data: Dict[str, Any],
    topic_name: str,
    output_file: Optional[str] = None,
    format: str = "markdown",
    ctx: Optional[Context] = None,
) -> str:
    """Generate a tax information report.

    Args:
        tax_data: Tax information data
        topic_name: Name of the tax topic
        output_file: Optional path to save the report
        format: Output format ('markdown' or 'csv')
        ctx: MCP context for logging

    Returns:
        str: The generated report
    """
    try:
        if ctx:
            await ctx.info(f"Generating report for {topic_name}")

        report = await generate_tax_report(tax_data, topic_name, output_file, format)
        return report
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to generate tax report: {e}")
        return f"Error generating report: {str(e)}"


def main():
    """Run the MCP server with CLI argument support."""
    parser = argparse.ArgumentParser(description="French Tax MCP Server")
    parser.add_argument("--sse", action="store_true", help="Use SSE transport")
    parser.add_argument("--streamable-http", action="store_true", help="Use StreamableHTTP transport (default)")
    parser.add_argument("--port", type=int, default=8888, help="Port to run the server on")

    args = parser.parse_args()

    # Set the port
    mcp.settings.port = args.port

    # Run server with appropriate transport
    if args.sse:
        mcp.run(transport="sse")
    elif args.streamable_http:
        # Use StreamableHTTP only when explicitly requested
        mcp.run(transport="streamable-http")
    else:
        # Default to stdio transport (faster and more reliable for MCP)
        mcp.run()


if __name__ == "__main__":
    main()
