# J-Tracker - Your Job Tracking Assistant

[![GitHub license](https://img.shields.io/github/license/CSC-510-G7/application-tracking-system)](https://github.com/CSC-510-G7/application-tracking-system/blob/63bc5b12d117220fc678f563f6fa8e6dc0074f1d/LICENSE)
[![DOI](https://zenodo.org/badge/426259091.svg)](https://zenodo.org/badge/latestdoi/426259091)
[![GitHub issues](https://img.shields.io/github/issues/CSC-510-G7/application-tracking-system)](https://github.com/CSC-510-G7/application-tracking-system/issues)
[![Github closes issues](https://img.shields.io/github/issues-closed-raw/CSC-510-G7/application-tracking-system)](https://github.com/CSC-510-G7/application-tracking-system/issues?q=is%3Aissue%20state%3Aclosed)
![GitHub top language](https://img.shields.io/github/languages/top/CSC-510-G7/application-tracking-system)

<p align="center"><img width="700" src="./resources/ApplicationTrackingAnimation.gif"></p>

The process of applying for jobs and internships is not a cakewalk. Managing job applications is a time-consuming process. Due to the referrals and deadlines, the entire procedure can be stressful. Our application allows you to track and manage your job application process, as well as regulate it, without the use of cumbersome Excel spreadsheets.

Our application keeps track of the jobs you've added to your wish list. It also keeps track of the companies you've already applied to and keeps a list of any rejections. Rather than having the user browse each company's site for potential prospects, our application allows the applicant to search for them directly using basic keywords. Any prospective work offers can then be added to the applicant's wishlist.

## New Features in Phase 4

### ⭐ Highlight - LLM Integration ⭐
Using Ollama, Qwen2.5 (1.5b) has been integrated into the system to support different language-heavy tasks:

1. Resume Tip Generation - Users can now get automated feedback on their resumes
2. Cover Letter Generation - Users can now get auto-generated cover letters, based on any uploaded resume and tailored to any given job description.

### Other new features
1. Upload and store multiple resumes for different purposes
2. Resume Viewer
3. UI Overhaul - Improved responsiveness, Navbar, Added logout confirmation, Added option to delete resume
4. Restructuring of backend - the single, massive backend file has been separated and organized by function
5. Restructured Docker-related files to simplify deployment
6. +60 More test cases

#### Bug fixes
1. Migrated job posting web scraper away from Google Jobs due to an update with Google's system preventing web scraping
  1a. Integrated headless browser using Selenium and ChromeDriver to scrape CareerBuilder instead
2. Users now stay logged in when refreshing the page
3. Support for Google Account logins has been fixed

---

### Application Demo video

🎥[Phase-4 Demo Video](https://github.com/CSC-510-G7/application-tracking-system/blob/ba6bae11a56878c46ec1d5e70d32e976c29c533d/resources/CSC-510-G7-jTracker.mp4)

## Table of contents

- [Basic Design](#basic-design)
- [Samples](#samples)
- [Future Scope](#future-scope)
- [Explanation](#explanation)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
  - [Requirements](#requirements)
  - [Steps to follow for the installation](#steps-to-follow-for-the-installation)
- [Hosting the Database](#hosting-the-database)
  - [Local MongoDB](#local-mongodb)
  - [Hosted database with MongoDB Atlas](#hosted-database-with-mongodb-atlas)
- [License](#license)
- [Funding](#funding)
- [How to Contribute](#how-to-contribute)
- [Team Members](#team-members)

## Basic Design:

![Basic Design](https://github.com/prithvish-doshi-17/application-tracking-system/blob/main/resources/Overall%20Design.PNG)

## Samples:

### Login Page / Signup Page

The introductory visual interface displayed from which a user is able to register and log into the application. User can also login or sign up through Google Authorization.

<p align="center"><img width="700" src="./resources/login_page.png"></p>
The Google Authorization Login:

<p align="center"><img width="700" src="./resources/googleauth.png"></p>

### HomeScreen - Profile Page

After Logging In, the Profile page of the user is displayed where the user details such as Name, Institution, email, phone number, address, skills, and more are shown.
Users can add or update information to their profile, such as their personal information, skills, preferred job locations, and their experience level.

<p align="center"><img width="700" src="./resources/profilepage.png"></p>

### SearchPage

The interface through which a user is able to search for specific jobs and apply on them through the 'Apply' button.

1. Navigate to Job search page, search for particular Job.
2. Click on Details button to see the Job Details
3. Click on Apply button which will redirect to the Job Apply link.

<p align="center"><img width="700" src="./resources/search_roles_companywise.png"></p> 
<p align="center"><img width="700" src="./resources/FindJobs.png"></p>
<p align="center"><img width="700" src="./resources/Job_Description.png"></p>

### ApplicationPage

The user is able to access different saved applications - Waitlisted applications, Waiting for Refereals, Applied Jobs, Application Status. The user can also add more jobs to track through this screen.

<p align="center"><img width="700" src="./resources/AddApplicationpage.png"></p>

### MatchesPage

On this page, user can see different jobs that would be recommended to them based on their profile and their preferences. User can apply for that position from this page too.

<p align="center"><img width="700" src="./resources/Recommendjobspage.png"></p>

### ManageResumePage

This page now allows for users to upload multiple resumes, get automated, LLM-powered feedback, and get auto-generated cover letters when given any job description.

<p align="center"><img width="700" src="./resources/resume management page.png"></p>
<p align="center"><img width="700" src="./resources/resume management page feedback.png"></p>
<p align="center"><img width="700" src="./resources/resume management page cover letter.png"></p>

## Future Scope:

**Short Term: 3 Months**
- Include links to university career fairs.
- Direct connection to Linkedin, allowing for the addition of job opportunities to the wishlist.
- Add cover letters to database.

**Medium Term: 6 Months**
- Add a notification system for important application releases and deadlines.
- Add a feature that allows users to attach these reminders to their Google calendar.
- An option to maintain separate profiles for job tracking.
- Use recently added LLM to autofill profile fields.

**Long Term: 12 Months**
- Integrate the database into docker.
- Add a chrome extension to track external job search progress.
- Add Recruiter log-in and home page to interact with job-seekers.

## Explanation:

Currently, we have five fundamental items in our project:

1. The SearchPage where users can search about the Job Postings
2. The MatchesPage where users get recommendation about the jobs according to their preferences
3. The ApplicationsPage where users can add and see the position they applied to and can update/delete the the information. Any details in any table can be modified at any time during the process
4. The ProfilePage where user can add his skills, experience level and preffered location. This information is used to recommend user jobs that require similar skillsets
5. The ManageResumePage where users can upload resumes and get automated LLM-powered feedback, as well as cover letter generation tailored to any job description.

## Technologies Used:

- Python
- Node.Js
- Flask
- MongoDB
- React
- Docker
- Ollama
- Langchain
- Selenium

## Installation:

### Requirements:

- [Python](https://www.python.org/downloads/) (recommended >= 3.8)
- [pip](https://pip.pypa.io/en/stable/installation/) (Latest version 21.3 used as of 11/3)
- [npm](https://nodejs.org/en/) (Latest version 6.14.4 used as of 11/3)
- [Docker-Desktop](https://www.docker.com/products/docker-desktop/) (Latest version as of 11/27)

### Steps to follow for the installation:

1. **Clone the Repository**
    - Use the command `git clone https://github.com/jashgopani/application-tracking-system.git` to clone the repository.

2. **Start the Docker Engine**
    - Ensure that Docker is installed on your system. If not, you can download it from the official Docker website.
    - Start the Docker engine on your machine. The command varies based on your operating system.

3. **Build Images and Start Program with Docker Compose**
    - Navigate to the project's root directory and build/start the system with the following command:
        ```
        docker compose up -d --build
        ```
    _(note: Although supporting Qwen2.5:1.5b doesn't require a GPU, it still occupies lots of memory when running locally, so be sure to minimize other processes for optimal performance)_

## Hosting the Database:

### Local MongoDB:

1. Download [MongoDB Community Server](https://docs.mongodb.com/manual/administration/install-community/)
2. Follow the [Installion Guide](https://docs.mongodb.com/guides/server/install/)
3. In app.py set 'host' string to 'localhost'
4. Run the local database:

mongodb

- Recommended: Use a GUI such as [Studio 3T](https://studio3t.com/download/) to more easily interact with the database

### Hosted database with MongoDB Atlas (RECOMMENDED):

1. [Create account](https://account.mongodb.com/account/register) for MongoDB

- **If current MongoDB Atlas owner adds your username/password to the cluster, skip to step 4** \*

2. Follow MongoDB Atlas [Setup Guide](https://docs.atlas.mongodb.com/getting-started/) to create a database collection for hosting applications
3. Create application.yml in the backend folder with the following content:
   ```
   GOOGLE_CLIENT_ID : <Oauth Google ID>
   GOOGLE_CLIENT_SECRET : <Oauth Google Secret>
   CONF_URL : https://accounts.google.com/.well-known/openid-configuration
   SECRET_KEY : <Any Secret You Want>
   USERNAME : <MongoDB Atlas Username>
   PASSWORD : <MongoDB Atlas Password>
   CLUSTER_URL : <MongoDB Cluster URL>
   ```
4. In app.py set 'host' string to your MongoDB Atlas connection string. Replace the username and password with {username} and {password} respectively
5. For testing through CI to function as expected, repository secrets will need to be added through the settings. Create individual secrets with the following keys/values:

MONGO_USER: <MongoDB Atlas cluster username>
MONGO_PASS: <MongoDB Atlas cluster password>

## License

The project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) license.

## Funding

This is an open source project that is free for use. Our team has not been sponsored in any way, nor are there any future plans for sponsorship.

## How to Contribute?

Please see our CONTRIBUTING.md for instructions on how to contribute to the repository and assist us in improving the project.

## Team Members

- Christopher Elchik
- Brandon Troy
- Kanchana Dhana Sadasivan

## Contact Info
For any questions, please email neerua08@gmail.com.
