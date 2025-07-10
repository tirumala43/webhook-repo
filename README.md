# webhook-repo
# GitHub Webhook to MongoDB and UI Display

This project implements a system to track GitHub repository activities (Push, Pull Request, Merge) using webhooks, store them in a MongoDB database, and display the latest changes on a clean, minimal web UI. [cite_start]The aim is to assess skills with a focus on bringing necessary, but minimal, data to the UI from a webhook receiver[cite: 3].

The project consists of two main GitHub repositories:
1.  [cite_start]`action-repo`: A GitHub repository where actions like "Push", "Pull Request", and "Merge" will be performed to trigger webhooks[cite: 5, 17].
2.  [cite_start]`webhook-repo`: Contains the Flask application acting as a webhook endpoint, MongoDB integration, and the UI[cite: 18].

## Project Structure (`webhook-repo`)

The `webhook-repo` follows a structured Flask application pattern for better organization and maintainability:

webhook-repo/
|----webhook-env/                         -Virtual environment to work with python and flask packages version etc 
|----static/                              
|       |-------css/
|                |----webhook.css         -Styling of page code in webhook.css 
|
|       |-------javascript/
|                 |----webhook.js         -Behavior of the web page 
|----templates/
|       |-------UI.html                   -HTML code resides here 
|----app.py                               - Flask application initializations code 
|----database.py                          - Database for mongodb connection 
|----routes.py                            - Defines the GitHub webhook endpoint
|----requirements.txt                     - tools requried to install specified in requriments or dependencies
|----README.md                            - Detailed project info 


## Features

* [cite_start]**GitHub Webhook Integration**: Automatically sends an event (webhook) on "Push", "Pull Request", and "Merge" actions to a registered endpoint[cite: 5].
* [cite_start]**Webhook Endpoint (Flask)**: A Python Flask application serves as the receiver for GitHub webhooks[cite: 25].
* [cite_start]**MongoDB Storage**: Stores received event data to MongoDB in a specified schema[cite: 5, 24].
* [cite_start]**Real-time UI Update**: The UI keeps pulling data from MongoDB every 15 seconds and displays the latest changes[cite: 6, 28, 39].
* **Dockerized Deployment**:  MongoDB are set up to run in Docker containers using `docker`.

## MongoDB Schema

[cite_start]The data is stored in MongoDB with the following schema[cite: 24, 27]:

| Field         | Datatype        | Details                                                                                     |
| :------------ | :-------------- | :------------------------------------------------------------------------------------------ |
| `id`          | `ObjectID`      | [cite_start]MongoDB default ID[cite: 27].                                                              |
| `request_id`  | `string`        | Use the Git commit hash directly. [cite_start]For Pull Requests, use the PR ID[cite: 27].              |
| `author`      | `string`        | [cite_start]Name of the GitHub user making that action[cite: 27].                                      |
| `action`      | `string`        | [cite_start]Name of the GitHub action: Is an Enum of ["PUSH", "PULL_REQUEST", "MERGE"][cite: 27].    |
| `from_branch` | `string`        | [cite_start]Name of Git branch in LHS (From action)[cite: 27].                                         |
| `to_branch`   | `string`        | [cite_start]Name of Git branch in RHS (To action)[cite: 27].                                           |
| `timestamp`   | `string(datetime)` | [cite_start]Must be a datetime formatted string (UTC) for the time of action[cite: 27].               |

## UI Display Formats

[cite_start]The UI displays the changes in specific formats[cite: 6]:

* [cite_start]**PUSH action**: `{author} pushed to {to_branch} on {timestamp}` [cite: 8]
    * [cite_start]*Sample*: "Travis" pushed to "staging" on 1st April 2021 - 9:30 PM UTC [cite: 9]
* [cite_start]**PULL_REQUEST action**: `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}` [cite: 11]
    * [cite_start]*Sample*: "Travis" submitted a pull request from "staging" to "master" on 1st April 2021 - 9:00 AM UTC [cite: 12]
* [cite_start]**MERGE action**: `{author} merged branch {from_branch} to {to_branch} on {timestamp}` [cite: 14]
    * [cite_start]*Sample*: "Travis" merged branch "dev" to "master" on 2nd April 2021 - 12:00 PM UTC [cite: 15]


## Setup and Running the Project

### Prerequisites

* **Docker** and **Docker Compose** installed on your system (WSL2 recommended for Windows users).
* **Git** installed.
* A **GitHub account** with the ability to create public repositories and configure webhooks.

### 1. `action-repo` Setup

1.  [cite_start]**Create a New GitHub Repository**: Create a **public** repository on GitHub named `action-repo`[cite: 17]. This will be your dummy repository where you perform Git actions.
2.  **Clone Locally**: If you haven't already, clone `action-repo` to your local machine.
    ```bash
    git clone [https://github.com/YourGitHubUsername/action-repo.git](https://github.com/YourGitHubUsername/action-repo.git)
    cd action-repo
    ```
3.  **Add a README.md**: (Optional but good practice) Add a simple `README.md` file to have some content.

### 2. `webhook-repo` Setup

1.  [cite_start]**Create a New GitHub Repository**: Create a **public** repository on GitHub named `webhook-repo`[cite: 18].
2.  **Clone Locally**:
    ```bash
    git clone [https://github.com/YourGitHubUsername/webhook-repo.git](https://github.com/YourGitHubUsername/webhook-repo.git)
    cd webhook-repo
    ```
3.  **Environment Variables**:
    * Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    * Edit the `.env` file and fill in the following details. Ensure you use strong secrets.
        ```dotenv
        MONGO_URI="mongodb://mongodb_container:27017/" # Connection string for MongoDB Docker service
        DB_NAME="github_events_db"
        COLLECTION_NAME="events"
        GITHUB_SECRET="your_strong_and_unique_github_webhook_secret_here" # CRITICAL: MUST match GitHub's secret
        FLASK_APP="app.py"
        FLASK_ENV="development" # Set to "production" for deployment
        ```

### 3. Run with Docker Compose

This is the recommended way to run the project, as it orchestrates both your Flask application and MongoDB in separate containers.

1.  **Build and Start Containers**: From the `webhook-repo` directory in your terminal:
    ```bash
    docker-compose up --build -d
    ```
    This command will:
    * Build the `flask_app` Docker image based on the `Dockerfile`.
    * Pull the `mongo` Docker image.
    * Create a Docker bridge network (`app_network`).
    * Start the `mongodb_container` and `flask_webhook_app` containers on this network.
    * Map port `5000` from the `flask_webhook_app` container to port `5000` on your host (WSL Ubuntu machine).
2.  **Verify Running Containers**:
    ```bash
    docker ps
    ```
    You should see `mongodb_container` and `flask_webhook_app` listed, with port `5000` mapped for the Flask app.
3.  **Check Flask App Logs (Optional but Recommended)**:
    ```bash
    docker logs flask_webhook_app
    ```
    You should see messages indicating Flask has started and successfully connected to MongoDB.

### 4. Configure GitHub Webhook

This crucial step connects your `action-repo` to your running Flask application. GitHub needs a publicly accessible URL to send webhook payloads.

1.  **Expose Flask App Publicly (for GitHub)**:
    Use a tunneling service like `ngrok` to expose your local Flask application to the internet.
    * Install `ngrok` if you haven't already.
    * In your WSL Ubuntu terminal (where your Docker containers are running), start `ngrok` for port `5000`:
        ```bash
        ngrok http 5000
        ```
    * `ngrok` will provide a public HTTPS URL (e.g., `https://xxxxxx.ngrok-free.app`). **Copy this URL.**
2.  **Add Webhook to `action-repo`**:
    * Go to your `action-repo` on GitHub in your web browser.
    * Navigate to **Settings** -> **Webhooks**.
    * Click the **Add webhook** button.
    * **Payload URL**: Paste the `ngrok` HTTPS URL you copied, appending `/webhook` to it (e.g., `https://xxxxxx.ngrok-free.app/webhook`).
    * **Content type**: Select `application/json`.
    * **Secret**: **PASTE THE EXACT SAME `GITHUB_SECRET`** you set in your `webhook-repo`'s `.env` file. This is crucial for webhook signature verification.
    * **Which events would you like to trigger this webhook?**: Select "Let me select individual events" and check:
        * `Pushes`
        * `Pull requests`
        * `Merges`
    * Ensure "Active" is checked.
    * Click **Add webhook**.

### 5. Access the UI

1.  Open your web browser and navigate to: `http://localhost:5000/`
    You should see the UI. Initially, it will likely display "No events recorded yet."

## Testing and Verification

[cite_start]Now, perform actions in your `action-repo` and observe how the webhooks trigger the Flask app, data is stored in MongoDB, and the UI updates every 15 seconds[cite: 6].

### Test 1: PUSH Action

1.  **Local Changes**: In your local `action-repo` directory, make a small change (e.g., edit `README.md`).
2.  **Commit and Push**:
    ```bash
    git add .
    git commit -m "Test: Initial push to trigger webhook"
    git push origin main # or master, depending on your default branch name
    ```
3.  **Verify**:
    * **GitHub**: Go to `action-repo` -> Settings -> Webhooks. Click on your webhook; you should see a recent successful delivery.
    * **Flask App Logs**: Check `docker logs flask_webhook_app` for messages indicating a "PUSH" event was received and processed.
    * [cite_start]**Your UI**: After a few seconds (up to 15 seconds due to polling), your UI at `http://localhost:5000/` should update with an entry like: `{YourGitHubUsername} pushed to main on {timestamp}`[cite: 8].

### Test 2: PULL_REQUEST Action (Opened)

1.  **Create New Branch**: In your local `action-repo` directory:
    ```bash
    git checkout -b feature/test-pr
    ```
2.  **Make Changes**: Create a new file or modify an existing one.
    ```bash
    echo "This content is for a new pull request." > pr_content.txt
    git add .
    git commit -m "Test: Adding file for PR"
    ```
3.  **Push New Branch**:
    ```bash
    git push origin feature/test-pr
    ```
4.  **Create PR on GitHub**: Go to your `action-repo` on GitHub. You should see a prompt to create a Pull Request from `feature/test-pr` to `main` (or `master`). Create the PR (do *not* merge it yet).
5.  **Verify**:
    * **GitHub**: Check webhook deliveries for a `pull_request` event.
    * **Flask Logs**: Look for messages about a "PULL_REQUEST" event being received.
    * [cite_start]**Your UI**: Your UI should update with an entry like: `{YourGitHubUsername} submitted a pull request from feature/test-pr to main on {timestamp}`[cite: 11].

### Test 3: MERGE Action

1.  **Merge the PR**: On the Pull Request page in your `action-repo` on GitHub, click "Merge pull request" and confirm.
2.  **Verify**:
    * [cite_start]**GitHub**: Check webhook deliveries again; there should be another `pull_request` event, which your Flask application's logic will interpret as a MERGE[cite: 13].
    * **Flask Logs**: You should see logs indicating a "MERGE" event was processed.
    * [cite_start]**Your UI**: Your UI should update with a new entry like: `{YourGitHubUsername} merged branch feature/test-pr to main on {timestamp}`[cite: 14].

## Stopping the Project

To stop and remove the Docker containers:

```bash
docker stop <container-id> 

```

## Visuals & Demos

This section provides visual aids and links to demonstrate the project's functionality.

### Screenshots

You can include screenshots of your UI and webhook logs here.

![UI Screenshot - Empty State](path/to/your/ui_empty_state.png)
*Description: Screenshot of the UI before any GitHub events are processed.*

![UI Screenshot - With Events](path/to/your/ui_with_events.png)
*Description: Screenshot of the UI displaying various GitHub events (Push, Pull Request, Merge).*

![GitHub Webhook Delivery Screenshot](path/to/your/github_webhook_delivery.png)
*Description: Screenshot from GitHub showing a successful webhook delivery.*

### Video Demonstrations

You can embed or link to short video demonstrations of the workflow.

**Project Demo (End-to-End Workflow)**
[![Project Demo Thumbnail](path/to/your/video_thumbnail.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)
*Description: A video showcasing the full workflow from a Git action to UI update.*

*(Replace `path/to/your/video_thumbnail.jpg` with a path to an image for your video thumbnail, and `https://www.youtube.com/watch?v=YOUR_VIDEO_ID` with the actual link to your YouTube or other video hosting platform.)*

### Important Links

Here are some important links related to the project.

* **`action-repo` on GitHub**: [https://github.com/YourGitHubUsername/action-repo](https://github.com/YourGitHubUsername/action-repo)
* **`webhook-repo` on GitHub**: [https://github.com/YourGitHubUsername/webhook-repo](https://github.com/YourGitHubUsername/webhook-repo)
* **MongoDB Documentation**: [https://docs.mongodb.com/](https://docs.mongodb.com/)
* **Flask Documentation**: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
* **GitHub Webhooks Documentation**: [https://docs.github.com/en/developers/webhooks-and-events/webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
* **ngrok**: [https://ngrok.com/](https://ngrok.com/)




