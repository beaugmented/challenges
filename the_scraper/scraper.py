import time
from datetime import datetime
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import platform
import os
import sys
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MonquiScraper:
    def __init__(self, headless=True):
        self.url = "https://monqui.com/"
        self.setup_driver(headless)
        
    def setup_driver(self, headless):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        
        # Add more options to avoid detection and improve stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Add a realistic user agent
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        try:
            # Use Selenium's built-in driver management
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            
            # Execute CDP commands to remove navigator.webdriver flag
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                """
            })
            
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            logger.error(traceback.format_exc())
            raise
        
    def scrape_events(self):
        try:
            logger.info(f"Navigating to {self.url}")
            self.driver.get(self.url)
            
            # Wait for the page to load completely
            time.sleep(5)  # Give the page a moment to fully render
            
            logger.info("Waiting for events section to load")
            
            # Save screenshot for debugging
            self.driver.save_screenshot("debug_screenshot.png")
            logger.info("Saved debug screenshot")
            
            # Log page source for debugging
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.info("Saved page source for debugging")
            
            events = []
            
            # Try to find "Just Announced" events which appear at the top
            try:
                just_announced_links = self.driver.find_elements(By.CSS_SELECTOR, "a.justAnnList")
                just_announced_dates = self.driver.find_elements(By.CSS_SELECTOR, "span.eventDateSpan")
                
                if just_announced_links and len(just_announced_links) == len(just_announced_dates):
                    logger.info(f"Found {len(just_announced_links)} 'Just Announced' events")
                    
                    for i, (link, date_span) in enumerate(zip(just_announced_links, just_announced_dates)):
                        try:
                            event_data = {}
                            
                            # Artist name from link text
                            event_data["artist"] = link.text.strip()
                            
                            # Date and venue from date span
                            date_venue_text = date_span.text.strip()
                            if date_venue_text:
                                parts = date_venue_text.split()
                                if len(parts) >= 2:
                                    # Format is typically "09/24 Wonder Ballroom"
                                    date_part = parts[0]
                                    venue_part = " ".join(parts[1:]).replace("<br>", "")
                                    
                                    event_data["date"] = date_part
                                    event_data["venue"] = venue_part
                                    
                                    # Try to parse the date
                                    if "/" in date_part:
                                        month, day = date_part.split("/")
                                        current_year = datetime.now().year
                                        event_data["full_date"] = f"{month}/{day}/{current_year}"
                            
                            # Get ticket link
                            event_data["ticket_link"] = link.get_attribute("href")
                            
                            # Default values for other fields
                            event_data["special_guest"] = None
                            event_data["show_time"] = None
                            event_data["door_time"] = None
                            event_data["price"] = None
                            event_data["age_restriction"] = None
                            event_data["sold_out"] = False
                            
                            events.append(event_data)
                        except Exception as e:
                            logger.error(f"Error processing 'Just Announced' event {i+1}: {e}")
                            continue
            except Exception as e:
                logger.warning(f"Error processing 'Just Announced' section: {e}")
            
            # Try to find regular event listings
            try:
                # Look for event containers with class "rhp-event-series"
                event_containers = self.driver.find_elements(By.CSS_SELECTOR, "div.rhp-event-series.rhp-widget-event-list")
                
                if event_containers:
                    logger.info(f"Found {len(event_containers)} event containers")
                    
                    for i, container in enumerate(event_containers):
                        try:
                            logger.info(f"Processing event container {i+1}/{len(event_containers)}")
                            event_data = {}
                            
                            # Artist/Event name - could be in a header or title element
                            try:
                                artist_element = container.find_element(By.CSS_SELECTOR, "h1, h2, h3, h4, .rhp-event__title")
                                event_data["artist"] = artist_element.text.strip()
                            except NoSuchElementException:
                                # Try alternate selectors
                                try:
                                    artist_element = container.find_element(By.CSS_SELECTOR, "strong, b, .title")
                                    event_data["artist"] = artist_element.text.strip()
                                except NoSuchElementException:
                                    event_data["artist"] = None
                            
                            # Date information
                            try:
                                date_container = container.find_element(By.CSS_SELECTOR, ".rhp-event__date--grid, .eventDateDetails")
                                date_text = date_container.text.strip()
                                event_data["full_date"] = date_text
                                
                                # Attempts to parse date components
                                # This would need to be adjusted based on the actual format
                                date_parts = date_text.split()
                                if len(date_parts) >= 3:
                                    event_data["day"] = date_parts[0]
                                    event_data["month"] = date_parts[1]
                                    event_data["date"] = date_parts[2]
                            except NoSuchElementException:
                                event_data["full_date"] = None
                                event_data["day"] = None
                                event_data["month"] = None
                                event_data["date"] = None
                            
                            # Venue
                            try:
                                venue_element = container.find_element(By.CSS_SELECTOR, ".venue, .location, .rhp-events-icon.location")
                                event_data["venue"] = venue_element.text.strip()
                            except NoSuchElementException:
                                event_data["venue"] = None
                            
                            # Ticket link or status
                            try:
                                cta_element = container.find_element(By.CSS_SELECTOR, ".rhp-event-cta a, a.btn")
                                event_data["ticket_link"] = cta_element.get_attribute("href")
                                
                                # Check if sold out
                                cta_text = cta_element.text.strip()
                                event_data["sold_out"] = "sold out" in cta_text.lower()
                            except NoSuchElementException:
                                event_data["ticket_link"] = None
                                event_data["sold_out"] = None
                            
                            # Additional info (these might need adjustment based on actual page structure)
                            event_data["special_guest"] = None
                            event_data["show_time"] = None
                            event_data["door_time"] = None
                            event_data["price"] = None
                            event_data["age_restriction"] = None
                            
                            events.append(event_data)
                        except Exception as e:
                            logger.error(f"Error processing event container {i+1}: {e}")
                            logger.error(traceback.format_exc())
                            continue
                else:
                    logger.warning("No event containers found with selector div.rhp-event-series.rhp-widget-event-list")
            except Exception as e:
                logger.error(f"Error processing event containers: {e}")
                logger.error(traceback.format_exc())
            
            # Try to extract events from a different page structure if needed
            if not events:
                logger.info("Attempting alternative event extraction")
                try:
                    # Try to find any links that contain '/event/' in their URLs
                    event_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/event/')]")
                    
                    if event_links:
                        logger.info(f"Found {len(event_links)} event links")
                        processed_urls = set()
                        
                        for link in event_links:
                            try:
                                url = link.get_attribute("href")
                                
                                # Skip if we've already processed this URL
                                if url in processed_urls:
                                    continue
                                processed_urls.add(url)
                                
                                # Basic information extraction
                                event_data = {
                                    "artist": link.text.strip() if link.text.strip() else None,
                                    "ticket_link": url,
                                    "full_date": None,
                                    "venue": None,
                                    "special_guest": None,
                                    "show_time": None,
                                    "door_time": None,
                                    "price": None,
                                    "age_restriction": None,
                                    "sold_out": False
                                }
                                
                                # Try to get contextual information
                                parent = link.find_element(By.XPATH, ".//..")
                                for _ in range(3):  # Check up to 3 levels of parent elements
                                    try:
                                        parent_text = parent.text
                                        # Look for common date formats (MM/DD, Month Day, etc.)
                                        if "/" in parent_text or any(month in parent_text.lower() for month in 
                                                                 ["jan", "feb", "mar", "apr", "may", "jun", 
                                                                  "jul", "aug", "sep", "oct", "nov", "dec"]):
                                            event_data["full_date"] = parent_text
                                            break
                                        
                                        # Try to move up to next parent
                                        parent = parent.find_element(By.XPATH, "./..")
                                    except Exception:
                                        break
                                
                                # Extract venue from URL structure
                                # URLs are often like: /event/artist-name/venue-name/location/
                                url_parts = url.split('/')
                                if len(url_parts) >= 5:
                                    venue_part = url_parts[-3]
                                    # Convert URL format to readable (e.g., "wonder-ballroom" -> "Wonder Ballroom")
                                    venue = ' '.join(word.capitalize() for word in venue_part.split('-'))
                                    event_data["venue"] = venue
                                
                                events.append(event_data)
                            except Exception as e:
                                logger.error(f"Error processing event link: {e}")
                                continue
                except Exception as e:
                    logger.error(f"Error in alternative event extraction: {e}")
                    logger.error(traceback.format_exc())
            
            return events
        
        except Exception as e:
            logger.error(f"Error scraping events: {e}")
            logger.error(traceback.format_exc())
            return []
        finally:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
    
    def save_to_json(self, events, filename="monqui_events.json"):
        with open(filename, "w") as f:
            json.dump(events, f, indent=4)
        logger.info(f"Saved {len(events)} events to {filename}")
    
    def save_to_csv(self, events, filename="monqui_events.csv"):
        df = pd.DataFrame(events)
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(events)} events to {filename}")

def main():
    logger.info("Starting Monqui events scraper...")
    try:
        scraper = MonquiScraper(headless=False)  # Set to True for headless mode
        events = scraper.scrape_events()
        
        logger.info(f"Found {len(events)} events")
        
        if events:
            scraper.save_to_json(events)
            scraper.save_to_csv(events)
            
            # Print sample of events
            for i, event in enumerate(events[:5]):
                logger.info(f"Event {i+1}: {event.get('artist')}")
                logger.info(f"Date: {event.get('full_date')}")
                logger.info(f"Venue: {event.get('venue')}")
                logger.info(f"Price: {event.get('price')}")
                logger.info(f"Sold out: {event.get('sold_out')}")
                logger.info("-" * 50)
        else:
            logger.warning("No events found. Check the selectors or website structure.")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
