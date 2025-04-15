# J-Tracker - Your Job Tracking Assistant

[![GitHub license](https://img.shields.io/github/license/SE25GroupProject/application-tracking-system)](https://github.com/SE25GroupProject/application-tracking-system/blob/main/LICENSE)
[![DOI](https://zenodo.org/badge/944599867.svg)](https://doi.org/10.5281/zenodo.15212578)
[![GitHub issues](https://img.shields.io/github/issues/SE25GroupProject/application-tracking-system)](https://github.com/CSC-510-G7/application-tracking-system/issues)
[![Github closes issues](https://img.shields.io/github/issues-closed-raw/SE25GroupProject/application-tracking-system)](https://github.com/SE25GroupProject/application-tracking-system/issues?q=is%3Aissue%20state%3Aclosed)
![GitHub top language](https://img.shields.io/github/languages/top/SE25GroupProject/application-tracking-system)
![Static Badge](https://img.shields.io/badge/style_checker-pylint-blue)
![Static Badge](https://img.shields.io/badge/code_formatter-black-blue)
![Static Badge](https://img.shields.io/badge/syntax_checker-black-blue)
![Static Badge](https://img.shields.io/badge/coverage_checker-coveralls-blue)
![Static Badge](https://img.shields.io/badge/testing-pytest-lime)
![Static Badge](https://img.shields.io/badge/pytest-8.3.4-lime)
[![Coverage Status](https://coveralls.io/repos/github/SE25GroupProject/application-tracking-system/badge.svg?branch=main)](https://coveralls.io/github/SE25GroupProject/application-tracking-system?branch=main)

<p align="center"><img width="700" src="./resources/ApplicationTrackingAnimation.gif"></p>

The process of applying for jobs and internships is not a cakewalk. Managing job applications is a time-consuming process. Due to the referrals and deadlines, the entire procedure can be stressful. Our application allows you to track and manage your job application process, as well as regulate it, without the use of cumbersome Excel spreadsheets.

Our application keeps track of the jobs you've added to your wish list. It also keeps track of the companies you've already applied to and keeps a list of any rejections. Rather than having the user browse each company's site for potential prospects, our application allows the applicant to search for them directly using basic keywords. Any prospective work offers can then be added to the applicant's wishlist.

## New Features
### Chrome Extension
Using our Chrome Extension you can now directly fill out your applications using your data from your profile here.
1. Saves time when filling out multiple applications
2. Data can be pulled from multiple profiles if you have different data for different applications
3. Works on multiple websites

### Other new features
1. Cover letter overhaul with new routes and testing
2. New frontend modals to support a cleaner UI
3. Increased testing and code coverage throughout
4. Restructuring of tests from a single file to seperate files designated by catagory
5. Allowed for multiple unique profiles

#### Bug fixes
1. Issues with resume feedback taking a long time
2. Issues with database models being incorrect
3. Issues with exceptions not being properly caught

---

### Application Demo video

[![Watch the Demo](https://img.youtube.com/vi/-0v_Mtghcqo/0.jpg)](https://youtu.be/-0v_Mtghcqo)

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

- **Notification System:** Implement alerts for application deadlines, new job postings, and status updates, with options to sync reminders to Google Calendar for better time management.
- **LinkedIn Integration:** Enable direct connection to LinkedIn for seamless import of profile details and the ability to add job opportunities to the wish list from LinkedIn postings.
- **Chrome Extension Enhancements:** Expand the Google Chrome extension to track job search activity across external sites and suggest relevant opportunities based on browsing history.
- **Recruiter Portal:** Introduce a dedicated recruiter login and interface to connect job seekers with hiring managers, facilitating direct communication and application submissions.
- **AI-Powered Profile Autofill:** Leverage AI to automatically populate user profiles with skills, experience, and preferences extracted from uploaded resumes or LinkedIn data, reducing manual setup time.

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

View our up-to-date installation instructions here: https://github.com/SE25GroupProject/application-tracking-system/blob/main/INSTALL.md

## License

The project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) license.

## Funding

This is an open source project that is free for use. Our team has not been sponsored in any way, nor are there any future plans for sponsorship.

## How to Contribute?

Please see our CONTRIBUTING.md for instructions on how to contribute to the repository and assist us in improving the project.

## Team Members

- Michael Sanchez
- Camille Jones
- Jacob Allard

## Contact Info
For any questions, please email neerua08@gmail.com.

# Repository Rubric:

### 📊 Score Card

#### Total Grade: 151

| Factor                                                                                                                                               | Score | Notes                                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ----------------------------------------------------------------------------------------------------------------- |
| Video                                                                                                                                                | 3     | https://youtu.be/-0v_Mtghcqo?si=jVyPmLhVGFJMkoP7                                                                |
| Workload                                                                                                                                             | 3     | Distributed                                                                                                       |
| Number of commits                                                                                                                                    | 3     | 50+                                                                                                               |
| Number of commits: by different people                                                                                                               | 3     | https://github.com/SE25GroupProject/application-tracking-system/graphs/contributors                                |
| Issues report: There are many                                                                                                                        | 3     | https://github.com/SE25GroupProject/application-tracking-system/issues                                             |
| Issues are being closed                                                                                                                              | 3     | https://github.com/SE25GroupProject/application-tracking-system/issues?q=is%3Aissue+is%3Aclosed                    |
| DOI badge                                                                                                                                            | 3     |  https://zenodo.org/records/15212579                                                                            |
| Docs: format                                                                                                                                         | 3     | https://github.com/SE25GroupProject/application-tracking-system/blob/main/.github/workflows/autopep8.yml           |
| Docs: description                                                                                                                                    | 3     | https://github.com/SE25GroupProject/application-tracking-system                                                    |
| Docs: short animated video                                                                                                                           | 3     |                                                                                                                   |
| Docs: strong punchlines                                                                                                                              | 3     | https://github.com/SE25GroupProject/application-tracking-system                                                   |
| Docs: mini tutorials                                                                                                                                 | 3     | https://github.com/SE25GroupProject/BurnoutExtreme/blob/master/Tutorials.md#signup-and-sign-in     |
| Use of version control tools                                                                                                                         | 3     | https://github.com/SE25GroupProject/application-tracking-system/blob/main/.github/workflows/autopep8.yml           |
| Use of style checkers                                                                                                                                | 3     | https://github.com/SE25GroupProject/BurnoutExtreme/blob/master/.github/workflows/autopep8.yml      |
| Use of code formatters.                                                                                                                              | 3     | https://github.com/SE25GroupProject/application-tracking-system/blob/main/.github/workflows/flake8.yml             |
| Use of syntax checkers.                                                                                                                              | 3     | https://github.com/SE25GroupProject/application-tracking-system?tab=readme-ov-file#style-checker-and-code-fomatter |
| Use of code coverage                                                                                                                                 | 3     | https://coveralls.io/github/SE25GroupProject/application-tracking-system?branch=main                               |
| Other automated analysis tools                                                                                                                       | 2     | https://github.com/SE25GroupProject/application-tracking-system/blob/main/.github/workflows/build.yml              |
| Test cases exist                                                                                                                                     | 3     | https://github.com/SE25GroupProject/application-tracking-system/tree/main/tests                                    |
| Test cases are routinely executed                                                                                                                    | 2     | https://github.com/SE25GroupProject/application-tracking-system/tree/main/tests                                    |
| The files http://contributing.md/ lists coding standards and lots of tips                                                                            | 3     |                                                                                                                   |
| Issues are discussed before they are closed                                                                                                          | 3     | https://github.com/SE25GroupProject/application-tracking-system/issues                                             |
| Chat channel: exists                                                                                                                                 | 3     | private discord group chat                                                                   |
| Test cases: a large proportion of the issues related to handling failing cases.                                                                      | 3     | https://github.com/SE25GroupProject/application-tracking-system/issues                                             |
| Evidence that the whole team is using the same tools                                                                                                 | 3     |                                                                                                                   |
| Evidence that the members of the team are working across multiple places in the code base                                                            | 3     | https://github.com/SE25GroupProject/application-tracking-system/pulse                                              |
| Short release cycles                                                                                                                                 | 3     |                                                                                                                   |
| Does your website and documentation provide a clear, high-level overview of your software?                                                           | 3     | https://github.com/SE25GroupProject/application-tracking-system                                                   |
| Does your website and documentation clearly describe the type of user who should use your software?                                                  | 3     | https://github.com/SE25GroupProject/application-tracking-system                                                   |
| Do you publish case studies to show how your software has been used by yourself and others?                                                          | 3     |                                                                                                                   |
| Is the name of your project/software unique?                                                                                                         | 3     | https://github.com/SE25GroupProject/application-tracking-system                                                  |
| Is your project/software name free from trademark violations?                                                                                        | 3     |                                                                                                                   |
| Is your software available as a package that can be deployed without building it?                                                                    | 3     | https://github.com/SE25GroupProject/application-tracking-system                                                    |
| Is your software available for free?                                                                                                                 | 3     | https://github.com/SE25GroupProject/application-tracking-system                                                    |
| Is your source code publicly available to download, either as a downloadable bundle or via access to a source code repository?                       | 3     | https://github.com/SE25GroupProject/application-tracking-system                                                   |
| Is your software hosted in an established, third-party repository like GitHub?                                                                       | 3     |                                                                                                                   |
| Is your documentation clearly available on your website or within your software?                                                                     | 3     |                                                                                                                   |
| Does your documentation include a "quick start" guide, that provides a short overview of how to use your software with some basic examples of use?   | 3     | https://github.com/SE25GroupProject/application-tracking-system                                                  |
| If you provide more extensive documentation, does this provide clear, step-by-step instructions on how to deploy and use your software?              | 3     |                                                                                                                   |
| Do you provide a comprehensive guide to all your software’s commands, functions and options?                                                         | 3     | https://github.com/SE25GroupProject/application-tracking-system                                                 |
| Do you provide troubleshooting information that describes the symptoms and step-by-step solutions for problems and error messages?                   | 3     |                                                                                                                   |
| If your software can be used as a library, package or service by other software, do you provide comprehensive API documentation?                     | 3     | https://github.com/SE25GroupProject/application-tracking-system/blob/main/INSTALL.md                               |
| Do you store your documentation under revision control with your source code?                                                                        | 2     |                                                                                                                   |
| Do you publish your release history e.g. release data, version numbers, key features of each release etc. on your web site or in your documentation? | 3     |                                                                                                                   |
| Does your software describe how a user can get help with using your software?                                                                        | 3     |                                                                                                                   |
| Does your website and documentation describe what support, if any, you provide to users and developers?                                              | 3     | https://github.com/SE25GroupProject/application-tracking-system/blob/main/INSTALL.md                               |
| Does your project have an e-mail address or forum that is solely for supporting users?                                                               | 3     |                                                                                                                   |
| Are e-mails to your support e-mail address received by more than one person?                                                                         | 3     |                                                                                                                   |
| Does your project have a ticketing system to manage bug reports and feature requests?                                                                | 2     | https://github.com/SE25GroupProject/application-tracking-system/issues                                             |
| Is your project's ticketing system publicly visible to your users, so they can view bug reports and feature requests?                                | 3     | https://github.com/SE25GroupProject/application-tracking-system/issues                                             |

# Software Sustainability Evaluation self-assessment table:


| Category                         | Question                                                                                                                                                                                                                                                                                                                      | Yes | No | Evidence |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- | -- | -------- |
| **Q1 - Software Overview**       |  |  |   |   |
|Question 1.1| Does your website and documentation provide a clear, high-level overview of your software?| ✅   |   |          |
|Question 1.2| Does your website and documentation clearly describe the type of user who should use your software?| ✅   |   |          |
|Question 1.3| Do you publish case studies to show how your software has been used by yourself and others?| ✅   |   |          |
| **Q2 - Identity**                | |  |   |   |
|Question 2.1| Is the name of your project/software unique?| ✅   |   |     [ ](https://github.com/SE25GroupProject/application-tracking-system/issues)    |
|Question 2.2| Is your project/software name free from trademark violations?| ✅   |   |          |
| **Q3 - Availability**            | |  |   |   |
|Question 3.1| Is your software available as a package that can be deployed without building it?| ✅   |   |          |
|Question 3.2| Is your software available for free?| ✅   |   |      https://github.com/SE25GroupProject/my-cookbook/issues    |
|Question 3.3| Is your source code publicly available to download, either as a downloadable bundle or via access to a source code repository?| ✅   |   |          |
| Question 3.4 | Is your software hosted in an established, third-party repository like [GitHub](https://github.com), [BitBucket](https://bitbucket.org), [LaunchPad](https://launchpad.net), or [SourceForge](https://sourceforge.net)? | ✅ |  | https://github.com/SE25GroupProject/application-tracking-system/issues|
| **Q4 - Documentation**           | |  |   |   |
|Question 4.1| Is your documentation clearly available on your website or within your software?| ✅   |   |     https://github.com/SE25GroupProject/application-tracking-system/issues     |
|Question 4.2| Does your documentation include a "quick start" guide, that provides a short overview of how to use your software with some basic examples of use?| ✅   |   |          |
|Question 4.3| If you provide more extensive documentation, does this provide clear, step-by-step instructions on how to deploy and use your software?| ✅   |   |    https://github.com/SE25GroupProject/application-tracking-system/issues      |
|Question 4.4| Do you provide a comprehensive guide to all your software’s commands, functions and options?| ✅   |   |          |
|Question 4.5| Do you provide troubleshooting information that describes the symptoms and step-by-step solutions for problems and error messages?| ✅   |   |          |
|Question 4.6| If your software can be used as a library, package or service by other software, do you provide comprehensive API documentation?| ✅   |   |          |
|Question 4.7| Do you store your documentation under revision control with your source code?| ✅   |   |          |
|Question 4.8| Do you publish your release history e.g. release data, version numbers, key features of each release etc. on your web site or in your documentation?| ✅   |   |          |
| **Q5 - Support**                 | |  |   |   |
|Question 5.1| Does your software describe how a user can get help with using your software?| ✅   |  |          |
|Question 5.2| Does your website and documentation describe what support, if any, you provide to users and developers?| ✅   |   |          |
|Question 5.3| Does your project have an e-mail address or forum that is solely for supporting users?| ✅   |   |          |
|Question 5.4| Are e-mails to your support e-mail address received by more than one person?| ✅   |   |          |
|Question 5.5| Does your project have a ticketing system to manage bug reports and feature requests?| ✅   |   |          |
|Question 5.6| Is your project's ticketing system publicly visible to your users, so they can view bug reports and feature requests?| ✅   |  | https://github.com/SE25GroupProject/application-tracking-system/issues         |
| **Q6 - Maintainability**         | |  |   |   |
|Question 6.1| Is your software’s architecture and design modular?| ✅   |   |          |
|Question 6.2| Does your software use an accepted coding standard or convention?| ✅   |   |          |
| **Q7 - Open Standards**          | |  |   |   |
|Question 7.1| Does your software allow data to be imported and exported using open data formats?| ✅   |   |          |
|Question 7.2| Does your software allow communications using open communications protocols?| ✅   |   |          |
| **Q8 - Portability**             | |  |   |   |
|Question 8.1| Is your software cross-platform compatible?| ✅   |   | We use docker         |
| **Q9 - Accessibility**           | |  |   |   |
|Question 9.1| Does your software adhere to appropriate accessibility conventions or standards?| ✅   |   |          |
|Question 9.2| Does your documentation adhere to appropriate accessibility conventions or standards?| ✅   |  |          |
| **Q10 - Source Code Management** | |  |   |   |
|Question 10.1| Is your source code stored in a repository under revision control?| ✅   |   |  https://github.com/SE25GroupProject/application-tracking-system      |
|Question 10.2| Is each source code release a snapshot of the repository?| ✅   |   |          |
|Question 10.3| Are releases tagged in the repository?| ✅   |  |          |
|Question 10.4| Is there a branch of the repository that is always stable? (i.e. tests always pass, code always builds successfully)| ✅   |   |  main branch        |
|Question 10.5| Do you back-up your repository?| ✅   |   |          |
| **Q11 - Building & Installing**  | |  |   |   |
|Question 11.1| Do you provide publicly-available instructions for building your software from the source code?| ✅   |   |          |
|Question 11.2| Can you build, or package, your software using an automated tool?| ✅   |   |          |
|Question 11.3| Do you provide publicly-available instructions for deploying your software?| ✅   |   | https://github.com/SE25GroupProject/application-tracking-system/blob/main/INSTALL.md         |
|Question 11.4| Does your documentation list all third-party dependencies?| ✅   |   |  https://github.com/SE25GroupProject/application-tracking-system/blob/main/api/requirements.txt        |
|Question 11.5| Does your documentation list the version number for all third-party dependencies?| ✅   |   |          |
|Question 11.6| Does your software list the web address, and licences for all third-party dependencies and say whether the dependencies are mandatory or optional?| ✅   |   |          |
|Question 11.7| Can you download dependencies using a dependency management tool or package manager?| ✅   |   |          |
|Question 11.8| Do you have tests that can be run after your software has been built or deployed to show whether the build or deployment has been successful?| ✅   |   |  Pytest        |
| **Q12 - Testing**                | |  |   |   |
|Question 12.1| Do you have an automated test suite for your software?| ✅   |   |  JUnit        |
|Question 12.2| Do you have a framework to periodically (e.g. nightly) run your tests on the latest version of the source code?| ✅   |   |  https://github.com/SE25GroupProject/application-tracking-system/tree/main/.github/workflows        |
|Question 12.3| Do you use continuous integration, automatically running tests whenever changes are made to your source code?| ✅   |   |  https://github.com/SE25GroupProject/application-tracking-system/tree/main/.github/workflows        |
|Question 12.4| Are your test results publicly visible?| ✅   |   |  https://github.com/SE25GroupProject/my-cookbook/tree/main/.github/workflows        |
|Question 12.5| Are all manually-run tests documented?| ✅   |   |          |
| **Q13 - Community Engagement**   |  |  |   |   |                                                                                                                                                                                           
|Question 13.1| Does your project have resources (e.g. blog, Twitter, RSS feed, Facebook page, wiki, mailing list) that are regularly updated with information about your software?| ✅   |   | https://github.com/SE25GroupProject/application-tracking-system/blob/main/README.md         |
|Question 13.2| Does your website state how many projects and users are associated with your project?| ✅   |   |          |
|Question 13.3| Do you provide success stories on your website?| ✅   |   |          |
|Question 13.4| Do you list your important partners and collaborators on your website?| ✅   |   |          |
|Question 13.5| Do you list your project's publications on your website or link to a resource where these are available?|    | ❌  | no publications         |
|Question 13.6| Do you list third-party publications that refer to your software on your website or link to a resource where these are available?|    | ❌ | no third party publications         |
|Question 13.7| Can users subscribe to notifications to changes to your source code repository?| ✅   |   |          |
|Question 13.8| If your software is developed as an open source project (and, not just a project developing open source software), do you have a governance model?| ✅   |   | https://github.com/SE25GroupProject/application-tracking-system/blob/main/LICENS          |
| **Q14 - Contributions**          ||  |   |   |
|Question 14.1| Do you accept contributions (e.g. bug fixes, enhancements, documentation updates, tutorials) from people who are not part of your project?| ✅   |   |          |
|Question 14.2| Do you have a contributions policy?| ✅   | https://github.com/SE25GroupProject/application-tracking-system/blob/main/CONTRIBUTING.md   |          |
|Question 14.3| Is your contributions' policy publicly available?| ✅   |   |          |
|Question 14.4| Do contributors keep the copyright/IP of their contributions?| ✅   |   |          |
| **Q15 - Licensing**              |  |  |   |   |                                                                                                                                                                                                                                 
|Question 15.1| Does your website and documentation clearly state the copyright owners of your software and documentation?| ✅   |   | https://github.com/SE25GroupProject/application-tracking-system/blob/main/LICENSE         |
|Question 15.2| Does each of your source code files include a copyright statement?| ✅   |   |          |
|Question 15.3| Does your website and documentation clearly state the licence of your software?| ✅   |   | https://github.com/SE25GroupProject/application-tracking-system/blob/main/LICENSE          |
|Question 15.4| Is your software released under an open source licence?| ✅   |   | https://github.com/SE25GroupProject/application-tracking-system/blob/main/LICENSE          |
|Question 15.5| Is your software released under an OSI-approved open-source licence?| ✅   |   |  https://github.com/SE25GroupProject/application-tracking-system/blob/main/LICENSE         |
|Question 15.6| Does each of your source code files include a licence header?| ✅   |   |          |
|Question 15.7| Do you have a recommended citation for your software?| ✅   |   |  https://github.com/SE25GroupProject/application-tracking-system/blob/main/LICENSE        |
| **Q16 - Future Plans**           |  |  |   |   |
|Question 16.1| Does your website or documentation include a project roadmap (a list of project and development milestones for the next 3, 6 and 12 months)?| ✅   |   | Future contributions on the poster         |
|Question 16.2| Does your website or documentation describe how your project is funded, and the period over which funding is guaranteed?|    | ❌  |  no funding        |
|Question 16.3| Do you make timely announcements of the deprecation of components, APIs, etc.?|    | ❌  | github won't be maintained by us       |
