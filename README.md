# OLX Scraper

A robust and generic web scraper for OLX India built with Python and Selenium. This scraper can extract listings from any category on OLX with human-like behavior to avoid detection.

## Features

- Generic scraping capability for any OLX category
- Human-like behavior (random scrolling, delays, mouse movements)
- Robust error handling and retry mechanism
- Detailed logging
- CSV output with timestamps
- Category-specific file naming
- Both UI and URL-based navigation
- Anti-detection measures

## Requirements

- Python 3.7+
- Chrome Browser
- ChromeDriver (automatically managed)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/maneesh-sk/olx_scraper.git
cd olx_scraper
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:
```bash
python olx_scraper.py
```

2. Enter the OLX category URL when prompted (or press Enter for motorcycles)
3. Enter the starting page number (default: 1)
4. Enter the maximum pages to scrape (press Enter for all pages)
5. Close any popups when prompted
6. The script will create two files:
   - A CSV file with the scraped data (e.g., `olx_motorcycles_20250307_144047.csv`)
   - A log file (`olx_scraper.log`) with detailed execution information

## Output Format

The scraper saves the following information for each listing:
- Title
- Price
- Details
- Location
- Listing Date
- Page Number

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE) 