"""
This module contains the routes for the job searching functionality.
"""

from flask import Blueprint, jsonify, request
from models import Users
from utils import get_userid_from_header
from config import config
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
    with webdriver.Remote(config["SELENIUM_URL"] + ":4444/wd/hub", options=options) as driver:

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
            results.append({"title": title, "company": company, "location": location, "type": job_type, "link": link, "id": link.split("/")[-1]})
        
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
        
        return [
            {
              "company": "Scale AI",
              "id": "J3R5G06ZWMK43M198Z2",
              "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
              "location": "New York, NY (Onsite)",
              "title": "Mission Software Engineer, Federal",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3R0QM763R58690DWZX",
              "link": "https://www.careerbuilder.com/job/J3R0QM763R58690DWZX",
              "location": "New York, NY (Onsite)",
              "title": "Senior Software Engineer, iOS",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3P1GR6L0P737L84WRR",
              "link": "https://www.careerbuilder.com/job/J3P1GR6L0P737L84WRR",
              "location": "New York, NY (Onsite)",
              "title": "Lead Software Engineer, Full Stack (Python, Spark, AWS)",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3N0XJ60LS9410VNCN3",
              "link": "https://www.careerbuilder.com/job/J3N0XJ60LS9410VNCN3",
              "location": "New York, NY (Onsite)",
              "title": "Senior Software Engineer (JavaScript)",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3W5Y25W8PN4WR9JNR1",
              "link": "https://www.careerbuilder.com/job/J3W5Y25W8PN4WR9JNR1",
              "location": "New York, NY (Onsite)",
              "title": "Senior Lead Software Engineer (Full Stack)",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3W0RM6V98VJLPB6S6N",
              "link": "https://www.careerbuilder.com/job/J3W0RM6V98VJLPB6S6N",
              "location": "New York, NY (Onsite)",
              "title": "Senior Software Engineer, Full Stack",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3P5PH6H8H28202GHDM",
              "link": "https://www.careerbuilder.com/job/J3P5PH6H8H28202GHDM",
              "location": "New York, NY (Onsite)",
              "title": "Senior Software Engineer, Full Stack (Enterprise Platforms Technology)",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3R7YJ6W8JRZFRZCWNM",
              "link": "https://www.careerbuilder.com/job/J3R7YJ6W8JRZFRZCWNM",
              "location": "New York, NY (Onsite)",
              "title": "Senior Lead Software Engineer, Full Stack (Java/Python)",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3N45F68YQB5S9NQX4B",
              "link": "https://www.careerbuilder.com/job/J3N45F68YQB5S9NQX4B",
              "location": "New York, NY (Onsite)",
              "title": "Senior Software Engineer",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3W1PF69V1Y7M7Y9QYK",
              "link": "https://www.careerbuilder.com/job/J3W1PF69V1Y7M7Y9QYK",
              "location": "New York, NY (Onsite)",
              "title": "Lead Software Engineer, Full Stack (Java/Python)",
              "type": "Full-Time"
            },
            {
              "company": "BAE Systems",
              "id": "J3Q0VG78V1YF31M32RR",
              "link": "https://www.careerbuilder.com/job/J3Q0VG78V1YF31M32RR",
              "location": "Paterson, NJ (Onsite)",
              "title": "Software Engineer- All Levels with Security Clearance",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3N3LV723SD1BD1VZ48",
              "link": "https://www.careerbuilder.com/job/J3N3LV723SD1BD1VZ48",
              "location": "New York, NY (Onsite)",
              "title": "Senior Software Engineer, Full Stack (Python, ML, JavaScript, AWS)",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3N0QW7199L9XL8PMBK",
              "link": "https://www.careerbuilder.com/job/J3N0QW7199L9XL8PMBK",
              "location": "New York, NY (Onsite)",
              "title": "Lead Software Engineer, Backend",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3S4HH73ZVZVSYVJP8X",
              "link": "https://www.careerbuilder.com/job/J3S4HH73ZVZVSYVJP8X",
              "location": "New York, NY (Onsite)",
              "title": "Lead Software Engineer (Python)",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3M3B86VZJL8DHZBFP7",
              "link": "https://www.careerbuilder.com/job/J3M3B86VZJL8DHZBFP7",
              "location": "New York, NY (Onsite)",
              "title": "Lead, Software Engineer (Backend) Python/AWS",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3R0YQ6NP6JQCK7S28R",
              "link": "https://www.careerbuilder.com/job/J3R0YQ6NP6JQCK7S28R",
              "location": "New York, NY (Onsite)",
              "title": "Lead Software Engineer (Python)",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3R0RC5WY9LBW1R7QK4",
              "link": "https://www.careerbuilder.com/job/J3R0RC5WY9LBW1R7QK4",
              "location": "New York, NY (Onsite)",
              "title": "Senior Software Engineer, Back End (Python, Go, AWS)",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3W0J963R6N41NH74YZ",
              "link": "https://www.careerbuilder.com/job/J3W0J963R6N41NH74YZ",
              "location": "New York, NY (Onsite)",
              "title": "Senior Software Engineer",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3V7T16BXCT65K4D612",
              "link": "https://www.careerbuilder.com/job/J3V7T16BXCT65K4D612",
              "location": "New York, NY (Onsite)",
              "title": "Lead Software Engineer, Back End",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3T2XW6527568BM3KHD",
              "link": "https://www.careerbuilder.com/job/J3T2XW6527568BM3KHD",
              "location": "New York, NY (Onsite)",
              "title": "Lead Software Engineer, DevOps",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3S65P61X01NX8TPPTC",
              "link": "https://www.careerbuilder.com/job/J3S65P61X01NX8TPPTC",
              "location": "New York, NY (Onsite)",
              "title": "Senior Software Engineer, Back End",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3R1W16BR4ZS5VXSNBP",
              "link": "https://www.careerbuilder.com/job/J3R1W16BR4ZS5VXSNBP",
              "location": "New York, NY (Onsite)",
              "title": "Lead Software Engineer, iOS",
              "type": "Full-Time"
            },
            {
              "company": "Google",
              "id": "J3T6VT65GVRNC0CGCTJ",
              "link": "https://www.careerbuilder.com/job/J3T6VT65GVRNC0CGCTJ",
              "location": "New York, NY (Onsite)",
              "title": "Senior Software Engineer, AI/ML Natural Language Processing, Google Cloud Platforms",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3P6BW6FZ0VCM59GH3Z",
              "link": "https://www.careerbuilder.com/job/J3P6BW6FZ0VCM59GH3Z",
              "location": "New York, NY (Onsite)",
              "title": "Lead Software Engineer, Back End (Java)",
              "type": "Full-Time"
            },
            {
              "company": "Capital One",
              "id": "J3P3X46H8P66TWM8THD",
              "link": "https://www.careerbuilder.com/job/J3P3X46H8P66TWM8THD",
              "location": "New York, NY (Onsite)",
              "title": "Lead Software Engineer, Python",
              "type": "Full-Time"
            }
        ]

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
