## Instructions
this is a scraper for monqui.com that scrapes the upcoming events and returns them in a JSON format.

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the scraper:

```bash
uvicorn main:app --reload
```

3. Test the API:

```bash
curl -X POST http://localhost:8000/scrape -H "Content-Type: application/json" -d '{"url": "https://monqui.com", "selectors": {"artist": "h3.eventTitle", "date": "span.eventDateSpan"}}'
```
