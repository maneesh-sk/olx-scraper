# OLX Scraper

A robust and generic web scraper for OLX India built with Python and Selenium. This scraper can extract listings from Motorcyles/Scooters categories on OLX with human-like behavior to avoid detection.

## Features

- Generic scraping capability
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

2. When prompted, enter the OLX category URL:
   - Go to OLX India website (https://www.olx.in)
   - Select your desired location (city/area)
   - Navigate to either Motorcycles or Scooters category
   - Copy the complete URL (e.g., https://www.olx.in/en-in/bengaluru_g4058803/motorcycles_c81)
   - Paste the URL when prompted (or press Enter for default: Bengaluru motorcycles)
3. Enter the starting page number (default: 1)
4. Enter the maximum pages to scrape (press Enter for all pages)
5. Close any popups when prompted
6. The script will create a CSV file with the scraped data (e.g., `olx_motorcycles_20250307_144047.csv`)

## Output Format

The scraper saves the following information for each listing:
- Title: The name/title of the listing
- Price: The price in INR (as integer)
- Year: Manufacturing year of the vehicle
- Kilometers: Distance traveled (e.g., "12017 km")
- Location: The area/locality of the listing
- Listing Date: When the item was listed (e.g., "Today", "Yesterday", "Feb 06")
- Page Number: The page number where this listing was found

Example row for a bike listing:
```csv
title,price,year,kilometers,location,listing_date,page_number
Royal Enfield Classic 350,125000,2022,15000 km,Koramangala,Today,1
```

## Supported Categories
Currently optimized for:
- Motorcycles
- Scooters

Note: The scraper is designed to work with vehicle listings and expects year and kilometers as details. For other categories, you may need to modify the code to handle different types of details.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE) 
