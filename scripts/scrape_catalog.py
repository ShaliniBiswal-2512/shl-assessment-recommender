import requests
from bs4 import BeautifulSoup
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATALOG_URL = "https://www.shl.com/en/assessments/catalog/"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "shl_catalog_scraped.json")
SEED_FILE = os.path.join(DATA_DIR, "shl_catalog.json")

def scrape_shl_catalog():
    """
    Attempts to scrape the SHL catalog. 
    SHL's website heavily relies on JS rendering and anti-bot measures,
    so this is a robust best-effort scraper that falls back to a verified seed file
    if live scraping is blocked or structural changes occur.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    assessments = []
    
    try:
        logger.info(f"Attempting to scrape {CATALOG_URL}")
        response = requests.get(CATALOG_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Hypothetical selector for assessment cards
        # Real structure may vary; typically cards have a class like 'assessment-card'
        cards = soup.find_all('div', class_='assessment-card')
        
        for card in cards:
            name_elem = card.find('h3')
            desc_elem = card.find('p', class_='description')
            link_elem = card.find('a', href=True)
            cat_elem = card.find('span', class_='category')
            
            if name_elem and link_elem:
                assessments.append({
                    "name": name_elem.get_text(strip=True),
                    "url": link_elem['href'] if link_elem['href'].startswith('http') else f"https://www.shl.com{link_elem['href']}",
                    "description": desc_elem.get_text(strip=True) if desc_elem else "Description not available",
                    "category": cat_elem.get_text(strip=True) if cat_elem else "General",
                    "skills_measured": [],  # Often requires deeper page navigation
                    "test_type": "Unknown",
                    "duration": "Variable"
                })
                
        if not assessments:
            logger.warning("Scraper found no assessments (possibly due to JS rendering or CAPTCHA). Falling back to seed catalog.")
            return fallback_to_seed()
            
        logger.info(f"Successfully scraped {len(assessments)} assessments.")
        return assessments
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}. Falling back to seed catalog.")
        return fallback_to_seed()

def fallback_to_seed():
    if os.path.exists(SEED_FILE):
        with open(SEED_FILE, 'r') as f:
            return json.load(f)
    return []

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    data = scrape_shl_catalog()
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
        
    logger.info(f"Saved {len(data)} assessments to {OUTPUT_FILE}")
