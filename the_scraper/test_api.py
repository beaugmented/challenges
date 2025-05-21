import requests
import json

def test_scrape_endpoint():
    url = "http://localhost:8000/scrape"
    
    # Example: scrape title and headings from Python.org
    payload = {
        "url": "https://www.python.org/",
        "selectors": {
            "title": "title",
            "main_heading": "h1",
            "subheadings": "h2",
            "menu_items": "#main-navigation li a"
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        
        # Pretty print the response
        print("Status Code:", response.status_code)
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
    except requests.RequestException as e:
        print(f"Error: {e}")

def test_monqui_events_endpoint():
    url = "http://localhost:8000/monqui/events"
    
    # Use headless mode for faster testing
    params = {
        "headless": "true"
    }
    
    try:
        print("Fetching Monqui events... (this may take a few moments)")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        total_events = data.get("total_events", 0)
        events = data.get("events", [])
        
        print(f"Status Code: {response.status_code}")
        print(f"Total Events Found: {total_events}")
        
        # Print sample of events
        if events:
            print("\nSample Events:")
            for i, event in enumerate(events[:3]):
                print(f"Event {i+1}: {event.get('artist')}")
                print(f"Date: {event.get('full_date')}")
                print(f"Venue: {event.get('venue')}")
                print(f"Price: {event.get('price')}")
                print("-" * 30)
        
    except requests.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing the Monqui Scraper API...")
    print("Make sure the API server is running before executing this test.")
    print("\n1. Testing General Scrape Endpoint:")
    print("-" * 40)
    test_scrape_endpoint()
    
    print("\n2. Testing Monqui Events Endpoint:")
    print("-" * 40)
    test_monqui_events_endpoint() 