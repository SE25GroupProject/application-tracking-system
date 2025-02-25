from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from fake_useragent import UserAgent
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def scrape_careerbuilder_jobs(keywords: str, company: str, location: str):
    # Generate a random User-Agent to evade bot detection
    ua = UserAgent()
    user_agent = ua.random

    # Set up Selenium with headless Chrome
    options = Options()
    options.add_argument("--headless")  # Run headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(f"user-agent={user_agent}")  # Fake User-Agent

    results = []

    print("Starting Chrome WebDriver...")
    with webdriver.Remote("http://localhost:4444/wd/hub", options=options) as driver:

        wait = WebDriverWait(driver, 10)
        print("Chrome WebDriver started.")

        driver.get(
            f"https://www.careerbuilder.com/jobs?&company_name={company}&keywords={keywords}&location={location.replace(' ', '+')}"
        )
        # job_listings = wait.until(
        #     EC.presence_of_all_elements_located(
        #         (By.CSS_SELECTOR, "li.data-results-content-parent")
        #     )
        # )
        job_listings = driver.find_elements(By.CSS_SELECTOR, "li.data-results-content-parent")
        for job in job_listings:
            title = job.find_element(By.CSS_SELECTOR, "div.data-results-title").text
            details = job.find_element(By.CSS_SELECTOR, "div.data-details")
            company = details.find_element(By.CSS_SELECTOR, "span:nth-child(1)").text
            location = details.find_element(By.CSS_SELECTOR, "span:nth-child(2)").text
            job_type = details.find_element(By.CSS_SELECTOR, "span:nth-child(3)").text
            link = job.find_element(
                By.CSS_SELECTOR, "a.data-results-content"
            ).get_attribute("href")
            results.append({"title": title, "company": company, "location": location, "job_type": job_type, "link": link})

        return results

# CareerBuilder jobs search URL
results = scrape_careerbuilder_jobs("software engineer", "Google", "San Fransisco")
print(*results, sep="\n\n")
print(len(results))
