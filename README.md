# Monqui Scraper

A web scraper for extracting event data from [Monqui](https://monqui.com/), an importer of live music events in the Pacific Northwest since 1983.

## Features

- Scrapes upcoming events data including artist, date, venue, price, etc.
- Provides a FastAPI endpoint for retrieving the data
- Exports data to JSON and CSV formats
- Option for headless or visible browser operation

## Installation

### Python Requirements

```bash
cd the_scraper
pip install -r requirements.txt
```

### JavaScript Requirements (if using the frontend)

```bash
bun install
```

## Usage

### Running the API Server

```bash
cd the_scraper
python main.py
```

The API will be available at http://localhost:8000 with the following endpoints:
- `/` - API welcome page
- `/docs` - Swagger UI documentation
- `/monqui/events` - Get all Monqui events (using Selenium)
- `/scrape` - General purpose scraping endpoint (using BeautifulSoup)

### Running the Scraper Directly

```bash
cd the_scraper
python scraper.py
```

This will:
1. Scrape the Monqui website
2. Save results to `monqui_events.json` and `monqui_events.csv` 
3. Display a summary of scraped events in the console

### Running the Tests

```bash
cd the_scraper
python test_api.py
```

## Technologies

- **Python**: Main programming language
- **Selenium**: For browser automation and dynamic content scraping
- **FastAPI**: For API endpoints
- **BeautifulSoup**: For static HTML parsing
- **Pandas**: For data manipulation and CSV export

## License

This project is open-source software.
