from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import uvicorn
import requests
from bs4 import BeautifulSoup
import traceback
from scraper import MonquiScraper

app = FastAPI(title="Monqui Scraper API")

class ScrapeRequest(BaseModel):
    url: HttpUrl
    selectors: dict[str, str] = {}

@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    """
    Scrape data from a given URL using provided CSS selectors.
    
    Returns the scraped data as a JSON object.
    """
    try:
        response = requests.get(str(request.url), timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        result = {
            "url": str(request.url),
            "data": {}
        }
        
        for key, selector in request.selectors.items():
            elements = soup.select(selector)
            if elements:
                # If multiple elements found, return list of text content
                if len(elements) > 1:
                    result["data"][key] = [elem.get_text(strip=True) for elem in elements]
                # If single element, return text content directly
                else:
                    result["data"][key] = elements[0].get_text(strip=True)
            else:
                result["data"][key] = None
        
        return result
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error fetching URL: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping error: {str(e)}"
        )

@app.get("/monqui/events")
async def get_monqui_events(headless: bool = True):
    """
    Scrape upcoming events from Monqui.com using Selenium.
    
    Returns a list of upcoming events with details like artist, date, venue, etc.
    """
    try:
        scraper = MonquiScraper(headless=headless)
        events = scraper.scrape_events()
        
        return {
            "total_events": len(events),
            "events": events
        }
    except StopIteration as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scraping Monqui events: {str(e)}"
        )

@app.get("/")
async def root():
    return {"message": "Welcome to Monqui Scraper API. Use /scrape endpoint to scrape data or /monqui/events to get Monqui events."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
