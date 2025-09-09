"""MarkItDown-based scraper for French tax data."""

import re
from typing import Dict, List, Optional
from markitdown import MarkItDown
from french_tax_mcp.scrapers.base_scraper import BaseScraper

class MarkItDownScraper(BaseScraper):
    """Scraper using MarkItDown for more robust HTML parsing."""
    
    def __init__(self):
        super().__init__()
        self.md = MarkItDown()
    
    def get_tax_brackets(self, year: Optional[int] = None) -> Dict:
        """Get tax brackets using MarkItDown."""
        try:
            url = "https://www.service-public.fr/particuliers/vosdroits/F1419"
            result = self.md.convert_url(url)
            brackets = self._parse_brackets_from_markdown(result.text_content)
            
            return {
                "status": "success",
                "data": {
                    "year": year or 2024,
                    "brackets": brackets
                },
                "source": "service-public.fr"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _parse_brackets_from_markdown(self, content: str) -> List[Dict]:
        """Parse tax brackets from markdown content."""
        brackets = []
        
        # Pattern for tax bracket tables
        pattern = r'(\d+(?:\s\d+)*)\s*€.*?(\d+(?:\s\d+)*)\s*€.*?(\d+(?:,\d+)?)\s*%'
        matches = re.findall(pattern, content)
        
        for match in matches:
            try:
                min_str, max_str, rate_str = match
                min_amount = int(min_str.replace(' ', ''))
                max_amount = int(max_str.replace(' ', '')) if max_str != '∞' else None
                rate = float(rate_str.replace(',', '.'))
                
                brackets.append({
                    "min": min_amount,
                    "max": max_amount,
                    "rate": rate
                })
            except ValueError:
                continue
        
        return brackets[:5]  # Limit results
