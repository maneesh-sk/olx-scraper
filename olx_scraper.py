# Import required libraries
import time
import random
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import re
from pprint import pprint
import json
import os
import csv

# Import Selenium related libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging to track what the script is doing
logging.basicConfig(
    level=logging.INFO,  # Show all info messages
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('olx_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OLXScraper:
    def __init__(self, base_url: str = None, headless: bool = False, use_proxy: bool = False):
        """
        Initialize the OLX scraper with necessary settings
        
        Args:
            base_url: The base URL of the OLX category to scrape
            headless: Whether to run Chrome in headless mode
            use_proxy: Whether to use a proxy server
        """
        # Get the base URL from user if not provided
        if not base_url:
            base_url = input("Please enter the OLX category URL to scrape (e.g., https://www.olx.in/en-in/bengaluru_g4058803/motorcycles_c81): ").strip()
        
        if not base_url.startswith("https://www.olx.in"):
            raise ValueError("Invalid URL. Please provide a valid OLX India URL.")
        
        self.base_url = base_url
        
        # Extract category name from URL for file naming
        try:
            # Extract category name from URL (e.g., 'motorcycles' from 'motorcycles_c81')
            self.category = base_url.split('/')[-1].split('_')[0]
        except:
            self.category = "items"  # fallback name
        
        # Set up Chrome options for Selenium
        self.chrome_options = Options()
        
        if headless:
            # Headless mode settings
            self.chrome_options.add_argument('--headless=new')
            self.chrome_options.add_argument('--disable-gpu')
        
        # Add arguments to make Chrome more stable and less detectable
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--start-maximized')
        
        # Set a realistic user agent
        self.chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        
        # Add proxy if requested
        if use_proxy:
            # You would need to set up your proxy details here
            proxy = "your-proxy-address:port"
            self.chrome_options.add_argument(f'--proxy-server={proxy}')
        
        # Add experimental options to make automation less detectable
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Cookie file path - make it category specific
        self.cookie_file = f'olx_{self.category}_cookies.json'
        
        # CSV file setup - make it category specific
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = f'olx_{self.category}_{timestamp}.csv'
        
        # Define headers based on common OLX listing attributes
        self.csv_headers = ['title', 'price', 'year', 'kilometers', 'location', 'listing_date', 'page_number']
        
        # Create CSV file with headers
        with open(self.csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.csv_headers)
            writer.writeheader()

    def _save_cookies(self, driver) -> None:
        """Save cookies to file"""
        if driver.get_cookies():
            with open(self.cookie_file, 'w') as f:
                json.dump(driver.get_cookies(), f)

    def _load_cookies(self, driver) -> None:
        """Load cookies from file if they exist"""
        try:
            if os.path.exists(self.cookie_file):
                with open(self.cookie_file, 'r') as f:
                    cookies = json.load(f)
                for cookie in cookies:
                    driver.add_cookie(cookie)
                driver.refresh()
        except Exception as e:
            logger.warning(f"Error loading cookies: {str(e)}")

    def _simulate_human_scroll(self, driver) -> None:
        """Simulate human-like scrolling behavior"""
        total_height = driver.execute_script("return document.body.scrollHeight")
        viewport_height = driver.execute_script("return window.innerHeight")
        current_position = 0
        
        while current_position < total_height:
            # Random scroll amount between 100 and 400 pixels
            scroll_amount = random.randint(100, 400)
            current_position = min(current_position + scroll_amount, total_height)
            
            # Scroll smoothly
            driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}})")
            
            # Random pause between 0.5 and 1.5 seconds
            time.sleep(random.uniform(0.5, 1.5))

    def _setup_driver(self) -> webdriver.Chrome:
        """Set up and return a Chrome WebDriver instance"""
        try:
            # Create a new Chrome driver instance
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.chrome_options
            )
            
            # Set page load timeout to 30 seconds
            driver.set_page_load_timeout(30)
            
            # Add script to make WebDriver less detectable
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                    
                    // Overwrite the 'chrome' property to make it look more realistic
                    window.chrome = {
                        runtime: {}
                    };
                    
                    // Add language and platform details
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                '''
            })
            
            return driver
        except Exception as e:
            logger.error(f"Failed to set up Chrome driver: {str(e)}")
            raise

    def _wait_for_element(self, driver, selector: str, timeout: int = 10) -> Optional[webdriver.remote.webelement.WebElement]:
        """Wait for an element to be present and visible"""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except TimeoutException:
            return None

    def _clean_price(self, price_text: str) -> int:
        """Convert price text (e.g., "₹ 45,000") to a number (45000)"""
        try:
            price = re.sub(r'[^\d]', '', price_text)
            return int(price) if price else 0
        except ValueError:
            return 0

    def wait_for_user_action(self, message: str) -> None:
        """Wait for user to perform an action and continue"""
        input(f"\n{message} Press Enter to continue...")
        logger.info(f"Resumed after user action: {message}")

    def get_total_pages(self, driver) -> int:
        """Get the total number of pages available"""
        try:
            # Find all page numbers
            page_elements = driver.find_elements(By.CSS_SELECTOR, 'a[data-aut-id="pageItem"]')
            if not page_elements:
                return 1
            
            # Get the last page number
            last_page = max(int(elem.text) for elem in page_elements if elem.text.isdigit())
            logger.info(f"Total pages found: {last_page}")
            return last_page
        except Exception as e:
            logger.error(f"Error getting total pages: {e}")
            return 1

    def save_to_csv(self, data: Dict, page_number: int) -> None:
        """Save a single listing to CSV file"""
        try:
            data['page_number'] = page_number
            with open(self.csv_filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_headers)
                writer.writerow(data)
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")

    def navigate_to_page_ui(self, driver, target_page: int) -> bool:
        """Try to navigate to a page using UI elements (more human-like)"""
        try:
            # Find the target page button
            page_buttons = driver.find_elements(By.CSS_SELECTOR, 'a[data-aut-id="pageItem"]')
            for button in page_buttons:
                if button.text.strip() == str(target_page):
                    # Move mouse to button (human-like)
                    ActionChains(driver).move_to_element(button).perform()
                    time.sleep(random.uniform(0.5, 1))
                    
                    # Click the button
                    button.click()
                    time.sleep(random.uniform(2, 3))
                    
                    # Verify we reached the correct page
                    current_url = driver.current_url
                    if "page=" in current_url:
                        current_page = int(re.search(r'page=(\d+)', current_url).group(1))
                        if current_page == target_page:
                            return True
                    
                    return False
            
            # If target page button not found, try using Next button
            next_button = driver.find_element(By.CSS_SELECTOR, 'a[data-aut-id="pagination-next"]')
            if next_button and next_button.is_displayed():
                next_button.click()
                time.sleep(random.uniform(2, 3))
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error in UI navigation: {e}")
            return False

    def navigate_to_page_url(self, driver, page_number: int) -> bool:
        """Navigate to a page using direct URL (fallback method)"""
        try:
            url = f"{self.base_url}?page={page_number}"
            driver.get(url)
            time.sleep(random.uniform(2, 4))
            
            current_url = driver.current_url
            if "page=" not in current_url:
                logger.error("URL navigation failed - redirected to main page")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error in URL navigation: {e}")
            return False

    def extract_listing_data(self, driver, listing_element, page_number: int) -> Optional[Dict]:
        """Extract data from a single listing"""
        try:
            # Extract basic information (common across all categories)
            title = listing_element.find_element(By.CSS_SELECTOR, 'div._2Gr10[data-aut-id="itemTitle"]').text.strip()
            
            try:
                price = self._clean_price(listing_element.find_element(By.CSS_SELECTOR, 'span._1zgtX[data-aut-id="itemPrice"]').text)
            except:
                price = 0
            
            try:
                details = listing_element.find_element(By.CSS_SELECTOR, 'div._21gnE[data-aut-id="itemSubTitle"]').text.strip()
                # First remove commas from numbers (e.g., "12,017 km" -> "12017 km")
                details = re.sub(r'(\d+),(\d+)', r'\1\2', details)
                # Split details by separators while preserving "km" with its number
                detail_parts = [d.strip() for d in re.split(r'\s*[-|]\s*', details) if d.strip()]
                
                # Initialize year and kilometers
                year = ""
                kilometers = ""
                
                # First part is typically the year
                if len(detail_parts) > 0:
                    year = detail_parts[0]
                # Second part typically contains the kilometers
                if len(detail_parts) > 1:
                    kilometers = detail_parts[1]
            except:
                year = ""
                kilometers = ""
            
            try:
                # Updated selector for location and date
                details_element = listing_element.find_element(By.CSS_SELECTOR, 'div._3VRSm[data-aut-id="itemDetails"]')
                full_text = details_element.text.strip()
                
                # Split text into parts
                parts = full_text.split('\n')
                
                # First part before == is location
                location = parts[0].split('==')[0].strip()
                
                # Last part is the date
                listing_date = parts[-1].strip()
            except:
                location = "Unknown"
                listing_date = "Unknown"
            
            data = {
                'title': title,
                'price': price,
                'year': year,
                'kilometers': kilometers,
                'location': location,
                'listing_date': listing_date
            }
            
            # Save to CSV immediately
            self.save_to_csv(data, page_number)
            
            # Enhanced logging with all important details
            details_str = ' | '.join(filter(None, [year, kilometers]))
            logger.info(f"Scraped: {data['title']} - ₹{data['price']:,} ({details_str}) ({data['location']}, {data['listing_date']})")
            
            return data
        except Exception as e:
            logger.error(f"Error extracting listing data: {e}")
            return None

    def scrape_listings(self, start_page: int = 1, max_pages: Optional[int] = None) -> None:
        """Main function to scrape listings across multiple pages"""
        driver = None
        try:
            logger.info("Starting OLX scraper...")
            driver = self._setup_driver()
            
            # Load first page
            driver.get(self.base_url)
            logger.info("Loaded first page")
            
            # Wait for user to handle initial popup
            self.wait_for_user_action("Please close any popups if present.")
            
            # If starting from a page other than 1, navigate there
            if start_page > 1:
                logger.info(f"Navigating to start page {start_page}")
                if not self.navigate_to_page_ui(driver, start_page):
                    logger.warning("UI navigation failed, trying direct URL...")
                    if not self.navigate_to_page_url(driver, start_page):
                        logger.error("Failed to reach start page. Exiting.")
                        return
            
            # Get total number of pages
            total_pages = self.get_total_pages(driver)
            if max_pages:
                total_pages = min(total_pages, max_pages)
            
            logger.info(f"Will scrape {total_pages} pages starting from page {start_page}")
            
            # Iterate through pages
            current_page = start_page
            while current_page <= total_pages:
                try:
                    logger.info(f"Processing page {current_page}/{total_pages}")
                    
                    # Find listings
                    listings = driver.find_elements(By.CSS_SELECTOR, 'div._2v8Tq')
                    logger.info(f"Found {len(listings)} listings on page {current_page}")
                    
                    # Process each listing
                    for idx, listing in enumerate(listings, 1):
                        try:
                            data = self.extract_listing_data(driver, listing, current_page)
                            if not data:
                                logger.warning(f"Failed to extract data for listing {idx} on page {current_page}")
                        except StaleElementReferenceException:
                            logger.warning(f"Listing {idx} on page {current_page} became stale, skipping...")
                            continue
                    
                    # Try UI navigation first
                    if current_page < total_pages:
                        navigation_successful = self.navigate_to_page_ui(driver, current_page + 1)
                        
                        # If UI navigation fails, try URL navigation
                        if not navigation_successful:
                            logger.warning("UI navigation failed, trying direct URL...")
                            if not self.navigate_to_page_url(driver, current_page + 1):
                                logger.error("Navigation failed. Stopping scraper.")
                                break
                    
                    current_page += 1
                    time.sleep(random.uniform(3, 6))
                    
                except Exception as e:
                    logger.error(f"Error processing page {current_page}: {e}")
                    self.wait_for_user_action("Error occurred. Please check if everything is okay.")
            
            logger.info("Scraping completed successfully!")
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            if driver:
                driver.quit()

def main():
    """Main function that runs the scraper"""
    try:
        # Get the base URL from user
        base_url = input("Enter the OLX category URL to scrape (press Enter for motorcycles): ").strip()
        if not base_url:
            base_url = "https://www.olx.in/en-in/bengaluru_g4058803/motorcycles_c81"
        
        # Initialize scraper with the provided URL
        scraper = OLXScraper(base_url=base_url, headless=False, use_proxy=False)
        
        # Ask user for scraping parameters
        start_page = int(input("Enter starting page number (default 1): ") or 1)
        max_pages = input("Enter maximum pages to scrape (press Enter for all pages): ")
        max_pages = int(max_pages) if max_pages else None
        
        # Add retry mechanism for resilience
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                scraper.scrape_listings(start_page=start_page, max_pages=max_pages)
                break
            except Exception as e:
                retry_count += 1
                logger.error(f"Attempt {retry_count} failed: {str(e)}")
                if retry_count < max_retries:
                    logger.info(f"Retrying in 30 seconds...")
                    time.sleep(30)
                else:
                    logger.error("Max retries reached. Please check the issues and try again.")
                    raise
        
        print(f"\nScraped data has been saved to: {scraper.csv_filename}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")

# This is the entry point of the script
if __name__ == "__main__":
    main()
