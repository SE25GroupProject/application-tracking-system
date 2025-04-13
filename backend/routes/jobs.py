"""
This module contains the routes for the job searching functionality.
"""

import random
from flask import Blueprint, jsonify, request
from models import Users
from utils import get_userid_from_header
from config import config

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent

jobs_bp = Blueprint("jobs", __name__)


def scrape_careerbuilder_jobs(keywords: str, company: str, location: str):
    """Scrapes career building site"""
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
    with webdriver.Remote(config["SELENIUM_URL"] + "/wd/hub", options=options) as driver:

        print("Chrome WebDriver started.")

        driver.get(
            f"https://www.careerbuilder.com/jobs?&company_name={company}&keywords={keywords}&location={location.replace(' ', '+')}"
        )
        # wait = WebDriverWait(driver, 3)
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
            results.append({
                "title": title,
                "company": company,
                "location": location,
                "type": job_type,
                "link": link,
                "externalId": link.split("/")[-1],
            })

        return results


@jobs_bp.route("/search", methods=["GET"])
def search():
    """
    Searches the web and returns the job postings for the given search filters

    :return: JSON object with job results
    """
    try:
        keywords = request.args.get("keywords", "")
        company = request.args.get("company", "")
        location = request.args.get("location", "")
        
        if not any([keywords, company, location]):
            return jsonify({"error": "At least one search parameter (keywords, company, or location) is required"}), 400

        results = scrape_careerbuilder_jobs(keywords, company, location)
        return jsonify(results), 200
    
    except Exception as err:
        print(f"Search error: {err}")
        return jsonify({"error": "Internal server error"}), 500


@jobs_bp.route("/getRecommendations", methods=["GET"])
def getRecommendations():
    """
    Scrapes jobs based on user's skills, job levels, and locations from the selected profile

    :return: JSON object with job results
    """
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()

        # Get the selected profile index from query parameter, default to user's default_profile
        selected_profile_idx = request.args.get("selected_profile", type=int, default=user.default_profile)

        # Validate the selected profile index
        if not user.profiles or selected_profile_idx < 0 or selected_profile_idx >= len(user.profiles):
            return jsonify({"error": "Invalid or no profile selected"}), 400

        # Get the selected profile
        selected_profile = user.profiles[selected_profile_idx]

        skill_sets = selected_profile.skills
        job_levels_sets = selected_profile.job_levels
        locations_set = selected_profile.locations

        if not skill_sets or not locations_set:
            return jsonify({"error": "No skills and/or locations found in selected profile"}), 400

        keywords = random.choice(skill_sets) + ' ' + (random.choice(job_levels_sets) if job_levels_sets else '')
        location = random.choice(locations_set)

        return scrape_careerbuilder_jobs(keywords, '', location)

    except TimeoutError as err:
        print(err)
        return jsonify({"error": "Internal server error"}), 500