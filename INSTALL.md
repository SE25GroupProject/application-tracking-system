# Installation

- [Requirements](#requirements)
- [Initial Steps](#steps-to-follow-for-the-installation)
- [Database](#hosting-the-database)
- [Google OAuth](#oauth-instructions)
- [Environment Variables](#environment-variables)
- [Final Steps](#final-steps)

## Requirements:

- [Python](https://www.python.org/downloads/) (recommended >= 3.8)
- [pip](https://pip.pypa.io/en/stable/installation/) (Latest version 21.3 used as of 11/3)
- [npm](https://nodejs.org/en/) (Latest version 6.14.4 used as of 11/3)
- [Docker-Desktop](https://www.docker.com/products/docker-desktop/) (Latest version as of 11/27)

## Initial Steps

1. **Clone the Repository**
   - Use the command `git clone https://github.com/SE25GroupProject/application-tracking-system.git` to clone the repository.

## Hosting the Database:

The database is hosted in a container named `mongodb`. This container name is used as the cluster url because all the containers are connected in a docker network. If the container name is ever changed, make sure to change the Cluster URL.

### Viewing Database

There are a number of ways to view the contents of the database.

1. **Mongo Express (Recommended)**

A mongo express container has been included in the docker compose file. This container is accessed at http://localhost:8081/. This page shows the databases and containers in the current mongodb instance. Variables for this instance are managed in the .env file, and will be mentioned in the [variables section](#environment-variables)

If this page is not working, check to make sure that all variables in your .env file are correct.

2. **Mongo Compass**

   1. Download Mongo Compass and Setup. [Download and Instructions here](https://www.mongodb.com/products/tools/compass).

   2. Create a new Connection With the following informaiton
      - host: localhost: `<MongoDB Container port>`
      - username: Username used in your .env file
      - password: Password used in your .env file
      - Authentication Source: admin
      - Your overall connection string should look like: `mongodb://<username>:<password>@<host>/`

3. **Mongo Shell**

   1. Using Docker Terminal

      1. Navigate to the tmp directory
         - `cd tmp`
      2. Use mongosh command
         - `mongosh`
      3. Input authentication details
         - `db.auth("<username>", "<password>")`

   2. Using local terminal
      - Use mongosh command with connection string
      - `mongosh mongodb://<username>:<password>@<host>/`

[Here is the documentation page for mongosh](https://www.mongodb.com/docs/mongodb-shell/)

## OAuth Instructions:

In order to get Google OAuth to work, there are a few different steps you will need to follow.

1. [Follow this link](https://console.developers.google.com/) to get to the Google API Site

2. Create a new project and name it.

3. On the overview page, click get started and fill out your app's information. Select the external option when prompted.

4. Go to the Clients tab and click "Create Client".

   - For the Application Type, Choose "Web Application"
   - For the **authorized Redirect URLs**, enter: `http://localhost:<API PORT>/users/signupGoogle/authorized`
     - Replace `<API PORT>` with the port that the api server uses. This can be checked in the docker-compose.yaml.
     - Make sure the path matches the URL path to [the Google Login Route](backend/routes/auth.py#:~:text=authorized_google). Right now, this is `/users/signupGoogle/authorized`
     - **Make sure to do this step!** Otherwise, you might get an error for mismatching reroute URLs.

5. Then click Create. The Client ID and Secret that is provided will be used during the [environment variables](#environment-variables) section, so remember to keep those around.

## Environment Variables

Do this step after you have completed the prior steps.

1. **Create .env file**

   - Create a .env file in the root directory. Add the following items to it:

     ```
     MONGO_INITDB_ROOT_USERNAME=<DB Username>
     MONGO_INITDB_ROOT_PASSWORD=<DB Password>
     CLUSTER_URL=<Name of Docker DB Container>
     ME_CONFIG_MONGODB_ADMINUSERNAME=<DB Username>
     ME_CONFIG_MONGODB_ADMINPASSWORD=<DB Password>
     ME_CONFIG_MONGODB_URL=mongodb://<DB Username>:<DB Password>@<Name of Docker DB Container>/
     ME_CONFIG_BASICAUTH=false
     ```

   - Replace `<DB Username>` with a username of your choice for the database
   - Replace `<DB Password>` with a password of your choice for the database
   - Replace `<Name of Docker DB Container>` with the name of the database container in the docker-compose.yaml

2. **Create backend yml file for variables**

   - Navigate to the backend folder and create a file named application.yml
   - Use the following template, and fill in the blanks for any key with brackets (<>)
     - Make sure to remove the brackets themselves

   ```
   GOOGLE_CLIENT_ID : <Oauth Google ID>
   GOOGLE_CLIENT_SECRET : <Oauth Google Secret>
   CONF_URL : https://accounts.google.com/.well-known/openid-configuration
   SECRET_KEY : <Any Secret You Want>
   ```

   - Use the Google Client Id and the Client Secret from [the Google OAuth section](#setup-google-oauth-client-id) to fill in `<Oauth Google ID>` and `<Oauth Google Secret>`
   - Change the secret key to anything else

## Final Steps

1. **Start the Docker Engine**

   - Ensure that Docker is installed on your system. If not, you can download it from the official Docker website.
   - Start the Docker engine on your machine. The command varies based on your operating system.
2. **Install Npm Packages**
   - Navigate to the project's frontend directory and install the packages with the following command:
     `npm install`

3. **Build Images and Start Program with Docker Compose**
   - Navigate to the project's root directory and build/start the system with the following command:
     `   docker compose up -d --build`
     _(note: Although supporting Qwen2.5:1.5b doesn't require a GPU, it still occupies lots of memory when running locally, so be sure to minimize other processes for optimal performance)_

## Installng the Chrome Extension

After the application is up and running, you should now set up the autofill extension inside of Google Chrome using the following steps:

1. **Navigate to chrome://extensions**<br>
   ![image](https://github.com/user-attachments/assets/7ec1b95e-af37-46a5-8a7b-d45fb5944970)

2. **Turn on Developer Mode**<br>
- This is located in the top right of the page.<br>
![image](https://github.com/user-attachments/assets/ff10f4ad-aafc-4ecb-bd1f-8a8f69203f90)

3. **Click "Load unpacked"**<br>
- This is a button that appears in the top left of the page after developer mode is activated.<br>
![image](https://github.com/user-attachments/assets/7c962905-9672-4030-8ff1-aaa1cf546ade)

4. **Navigate to the "chromeExtension" folder in the root of the project, and click "Select Folder"**<br>
![image](https://github.com/user-attachments/assets/698dd51a-da79-4d86-934e-c06866f26e6c)

You are now ready to autofill applications!

