import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import time


class GoogleScraper:
    def __init__(self, query, num_scrolls=2, headless=True):
        """
        Initialize the GoogleScraper.

        :param query: Search query string.
        :param num_scrolls: Number of scrolls to load more search results.
        :param headless: Whether to run Chrome in headless mode.
        """
        self.query = query
        self.num_scrolls = num_scrolls
        self.results = []
        self.driver = self._init_driver(headless)

    @staticmethod
    def _init_driver(headless):
        """
        Initialize the Chrome WebDriver with the required options.

        :param headless: Whether to run Chrome in headless mode.
        :return: WebDriver instance.
        """
        chrome_options = Options()
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        try:
            driver = webdriver.Chrome(service=Service(), options=chrome_options)
            return driver
        except WebDriverException as e:
            print(f"[ERROR]: WebDriver initialization failed: {e}")
            raise

    def scrape(self):
        """
        Perform Google search and scrape search result titles, URLs, and descriptions.
        """
        print("[INFO]: Starting Google scraping...")
        try:
            self.driver.get(f"https://www.google.com/search?q={self.query}")
            time.sleep(2)

            # Scroll down the page multiple times
            for _ in range(self.num_scrolls):
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                time.sleep(2)

            # Locate all search results
            search_results = self.driver.find_elements(By.CSS_SELECTOR, "div.g")
            print(f"[INFO]: Found {len(search_results)} search results.")

            for result in search_results:
                try:
                    title_element = result.find_element(By.CSS_SELECTOR, "h3")
                    url_element = result.find_element(By.CSS_SELECTOR, "a")
                    description_element = result.find_element(By.CSS_SELECTOR, "div.VwiC3b")

                    title = title_element.text
                    url = url_element.get_attribute("href")
                    description = description_element.text

                    if title and url:  # Skip if title or URL is missing
                        self.results.append({"Title": title, "URL": url, "Description": description})
                except NoSuchElementException:
                    print("[WARNING]: Missing element in a result, skipping...")

        except Exception as e:
            print(f"[ERROR]: An error occurred during scraping: {e}")
        finally:
            self.driver.quit()
            print("[INFO]: Scraping completed.")

    def save_to_csv(self, file_name="google_results.csv"):
        """
        Save the scraped results to a CSV file.

        :param file_name: Name of the CSV file to save results.
        """
        if not self.results:
            print("[WARNING]: No results to save.")
            return

        try:
            df = pd.DataFrame(self.results)
            df.to_csv(file_name, index=False)
            print(f"[INFO]: Results saved to {file_name}")
        except Exception as e:
            print(f"[ERROR]: Failed to save results to CSV: {e}")

if __name__ == "__main__":
    search_query = input("Enter search query: ").strip()
    try:
        num_scrolls = int(input("Enter number of scrolls (default 2): ").strip() or 2)
    except ValueError:
        print("[WARNING]: Invalid input for scrolls, defaulting to 2.")
        num_scrolls = 2

    # Initialize the scraper
    scraper = GoogleScraper(query=search_query, num_scrolls=num_scrolls, headless=True)

    # Perform scraping and save the results
    scraper.scrape()
    scraper.save_to_csv("google_search_results.csv")


    # contact 9511210785
