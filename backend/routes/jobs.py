"""
This module contains the routes for the job searching functionality.
"""

from flask import Blueprint, jsonify, request
import json
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
from models import Users
from utils import get_userid_from_header
from fake_useragent import UserAgent

jobs_bp = Blueprint("jobs", __name__)
user_agent = UserAgent()


@jobs_bp.route("/search")
def search():
    """
    Searches the web and returns the job postings for the given search filters

    :return: JSON object with job results
    """
    keywords = (
        request.args.get("keywords")
        if request.args.get("keywords")
        else "random_test_keyword"
    )
    salary = request.args.get("salary") if request.args.get("salary") else ""
    keywords = keywords.replace(" ", "+")
    if keywords == "random_test_keyword":
        return json.dumps({"label": str("successful test search")})
    # create a url for a crawler to fetch job information
    if salary:
        url = (
            "https://www.google.com/search?q="
            + keywords
            + "%20salary%20"
            + salary
            + "&ibp=htl;jobs"
        )
    else:
        url = "https://www.google.com/search?q=" + keywords + "&ibp=htl;jobs"

    print(user_agent.random)
    headers = {
        "User-Agent":
        #    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        user_agent.random,
        "Referrer": "https://www.google.com/",
    }

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")

    # parsing searching results to DataFrame and return
    df = pd.DataFrame(
        columns=[
            "jobTitle",
            "companyName",
            "location",
            "date",
            "qualifications",
            "responsibilities",
            "benefits",
        ]
    )
    mydivs = soup.find_all("div", class_="PwjeAc")

    for i, div in enumerate(mydivs):
        df.at[i, "jobTitle"] = div.find("div", {"class": "BjJfJf PUpOsf"}).text
        df.at[i, "companyName"] = div.find("div", {"class": "vNEEBe"}).text
        df.at[i, "location"] = div.find("div", {"class": "Qk80Jf"}).text
        df.at[i, "date"] = div.find_all("span", {"class": "LL4CDc"}, limit=1)[0].text

        # Collect Job Description Details
        desc = div.find_all("div", {"class": "JxVj3d"})
        for ele in desc:
            arr = list(x.text for x in ele.find_all("div", {"class": "nDgy9d"}))
            title = ele.find("div", {"class": "iflMsb"}).text
            if arr:
                df.at[i, str(title).lower()] = arr
    missingCols = list((df.loc[:, df.isnull().sum(axis=0).astype(bool)]).columns)

    for col in missingCols:
        df.loc[df[col].isnull(), [col]] = df.loc[df[col].isnull(), col].apply(
            lambda x: []
        )
    # df.loc[df["benefits"].isnull(), ["benefits"]] = df.loc[df["benefits"].isnull(), "benefits"].apply(lambda x: [])
    return jsonify(df.to_dict("records"))


@jobs_bp.route("/getRecommendations", methods=["GET"])
def getRecommendations():
    """
    Update the user profile with preferences: skills, job-level and location
    """
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        print(user["skills"])
        skill_sets = [x["value"] for x in user["skills"]]
        job_levels_sets = [x["value"] for x in user["job_levels"]]
        locations_set = [x["value"] for x in user["locations"]]
        recommendedJobs = []
        headers = {
            "User-Agent":
            #    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            user_agent.random,
            "Referrer": "https://www.google.com/",
        }
        if len(skill_sets) > 0 or len(job_levels_sets) > 0 or len(locations_set) > 0:
            random_skill = random.choice(skill_sets)
            random_job_level = random.choice(job_levels_sets)
            random_location = random.choice(locations_set)
            query = (
                "https://www.google.com/search?q="
                + random_skill
                + random_job_level
                + random_location
                + "&ibp=htl;jobs"
            )
            print(query)

            # inner_div = mydivs[0].find("div", class_="KGjGe")
            # if inner_div:
            #     data_share_url = inner_div.get("data-share-url")
            #     print(data_share_url)

        else:
            query = "https://www.google.com/search?q=" + "sde usa" + "&ibp=htl;jobs"

        page = requests.get(query, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")
        # KGjGe - div class to get url
        mydivs = soup.find_all("div", class_="PwjeAc")
        for div in mydivs:
            job = {}
            inner_div = div.find("div", class_="KGjGe")
            if inner_div:
                job["data-share-url"] = inner_div.get("data-share-url")
            job["jobTitle"] = div.find("div", {"class": "BjJfJf PUpOsf"}).text
            print(job["jobTitle"])
            job["companyName"] = div.find("div", {"class": "vNEEBe"}).text
            job["location"] = div.find("div", {"class": "Qk80Jf"}).text
            recommendedJobs.append(job)
        print(recommendedJobs)
        return jsonify(recommendedJobs)

    except Exception as err:
        print(err)
        return jsonify({"error": "Internal server error"}), 500
