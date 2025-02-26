"""
This module contains the routes for the job searching functionality.
"""

from flask import Blueprint, jsonify, request
from models import Users
from utils import get_userid_from_header
from fake_useragent import UserAgent
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from fake_useragent import UserAgent
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

jobs_bp = Blueprint("jobs", __name__)


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

        wait = WebDriverWait(driver, 3)
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
            results.append({"title": title, "company": company, "location": location, "type": job_type, "link": link, id: link.split("/")[-1]})
        
        return results


@jobs_bp.route("/search", methods=["GET"])
def search():
    """
    Searches the web and returns the job postings for the given search filters

    :return: JSON object with job results
    """
    try:
        keywords = request.args.get("keywords")
        company = request.args.get("company")
        location = request.args.get("location")
        return scrape_careerbuilder_jobs(keywords, company, location)
    
    except Exception as err:
        print(err)
        return jsonify({"error": "Internal server error"}), 500
    

@jobs_bp.route("/getRecommendations", methods=["GET"])
def getRecommendations():
    """
    Scrapes jobs based on user's skills, job levels, and locations
    
    :return: JSON object with job results
    """
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        print(user["skills"])
        skill_sets = [x["value"] for x in user["skills"]]
        job_levels_sets = [x["value"] for x in user["job_levels"]]
        locations_set = [x["value"] for x in user["locations"]]
        
        if not skill_sets or not locations_set:
            return jsonify({"error": "No skills and/or locations found"}), 400
        
        keywords = random.choice(skill_sets) + ' ' + (random.choice(job_levels_sets) if len(job_levels_sets) > 0 else '')
        location = random.choice(locations_set)
        
        return scrape_careerbuilder_jobs(keywords, '', location)

    except Exception as err:
        print(err)
        return jsonify({"error": "Internal server error"}), 500
