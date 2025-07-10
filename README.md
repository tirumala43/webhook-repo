# webhook-repo
# GitHub Webhook to MongoDB and UI Display

This project implements a system to track GitHub repository activities (Push, Pull Request, Merge) using webhooks, store them in a MongoDB database, and display the latest changes on a clean, minimal web UI. [cite_start]The aim is to assess skills with a focus on bringing necessary, but minimal, data to the UI from a webhook receiver.

The project consists of two main GitHub repositories:
1.  `action-repo`: A GitHub repository where actions like "Push", "Pull Request", and "Merge" will be performed to trigger webhooks[cite: 5, 17].
2.  `webhook-repo`: Contains the Flask application acting as a webhook endpoint, MongoDB integration, and the UI[cite: 18].

## Project Structure (`webhook-repo`)

The `webhook-repo` follows a structured Flask application pattern for better organization and maintainability:

<img width="1228" height="387" alt="Screenshot (475)" src="https://github.com/user-attachments/assets/e1b4b4ad-d6d5-4285-ac0d-9f5098a82884" />


## Features

**GitHub Webhook Integration**: Automatically sends an event (webhook) on "Push", "Pull Request", and "Merge" actions to a registered endpoint[cite: 5].
**Webhook Endpoint (Flask)**: A Python Flask application serves as the receiver for GitHub webhooks[cite: 25].
**MongoDB Storage**: Stores received event data to MongoDB in a specified schema[cite: 5, 24].
**Real-time UI Update**: The UI keeps pulling data from MongoDB every 15 seconds and displays the latest changes[cite: 6, 28, 39].
**Dockerized Deployment**:  MongoDB are set up to run in Docker containers using `docker`.

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

The UI displays the changes in specific formats:

* **PUSH action**: `{author} pushed to {to_branch} on {timestamp}`
    * *Sample*: "Travis" pushed to "staging" on 1st April 2021 - 9:30 PM UTC
* **PULL_REQUEST action**: `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}` 
    * *Sample*: "Travis" submitted a pull request from "staging" to "master" on 1st April 2021 - 9:00 AM UTC 
* **MERGE action**: `{author} merged branch {from_branch} to {to_branch} on {timestamp}` 
    * *Sample*: "Travis" merged branch "dev" to "master" on 2nd April 2021 - 12:00 PM UTC 


## Setup and Running the Project

### Prerequisites

* **Docker**  installed on your system (WSL2 recommended for Windows users).
* **Git** installed.
* A **GitHub account** with the ability to create public repositories and configure webhooks.

### 1. `action-repo` Setup

1.  **Create a New GitHub Repository**: Create a **public** repository on GitHub named `action-repo`[cite: 17]. This will be your dummy repository where you perform Git actions.
2.  **Clone Locally**: If you haven't already, clone `action-repo` to your local machine.
    ```bash
    git clone [https://github.com/YourGitHubUsername/action-repo.git](https://github.com/YourGitHubUsername/action-repo.git)
    cd action-repo
    ```
3.  **Add a README.md**: (Optional but good practice) Add a simple `README.md` file to have some content.

### 2. `webhook-repo` Setup

1.  **Create a New GitHub Repository**: Create a **public** repository on GitHub named `webhook-repo`.
2.  **Clone Locally**:
    ```bash
    git clone [https://github.com/YourGitHubUsername/webhook-repo.git](https://github.com/YourGitHubUsername/webhook-repo.git)
    cd webhook-repo
    ```
3.  **Environment Variables**:
  
    * Edit the `.env` file and fill in the following details. Ensure you use strong secrets.
        ```dotenv
        MONGO_URI="mongodb://mongodb_container:27017/" # Connection string for MongoDB Docker service
        DB_NAME="github_events_db"
        COLLECTION_NAME="events"
        ```

### 3. Run with Docker Compose

This is the recommended way to run the project, as it orchestrates both your Flask application and MongoDB in separate containers.

1.  **Build and Start Containers**: From the `webhook-repo` directory in your terminal:
    ```bash
    docker run -it -d --name mymongodb -p 27017:27017 mongo 
    ```
    This command will:
    * Pull the `mongo` Docker image.
    * Start the `mongodb_container` to test its connectivity and working
    * Map port `27017` from the `mongodb ` container to port `27017` on your host (WSL Ubuntu machine).
2.  **Verify Running Containers**:
    ```bash
    docker ps
    ```
    You should see `mongodb_container` and `flask_webhook_app` listed, with port `5000` mapped for the Flask app.
3.  **Check Flask App Logs (Optional but Recommended)**:
    ```bash
    docker logs mongodb
    ```
    You should see messages indicating MongoDB has started  successfully.

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

Now, perform actions in your `action-repo` and observe how the webhooks trigger the Flask app, data is stored in MongoDB, and the UI updates every 15 seconds.

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
    * **Flask App in Vscode client:  Verify that application running and test using curl commands and postman api testing
    * **Your UI**: After a few seconds (up to 15 seconds due to polling), your UI at `http://localhost:5000/` should update with an entry like: `{YourGitHubUsername} pushed to main on {timestamp}`.

### Test 2: PULL_REQUEST Action (Opened)

1.  **Create New Branch**: In your local `action-repo` directory:
    ```bash
    git checkout -b feature/login
    ```
2.  **Make Changes**: Create a new file or modify an existing one.
    ```bash
    echo "This content is for a new pull request." > login.txt
    git add .
    git commit -m "Test: Adding file for PR"
    ```
3.  **Push New Branch**:
    ```bash
    git push origin feature/login
    ```
4.  **Create PR on GitHub**: Go to your `action-repo` on GitHub. You should see a prompt to create a Pull Request from `feature/login` to `main` (or `master`). Create the PR (do *not* merge it yet).
5.  **Verify**:
    * **GitHub**: Check webhook deliveries for a `pull_request` event.
    * **Flask Logs**: Look for messages about a "PULL_REQUEST" event being received.
    * **Your UI**: Your UI should update with an entry like: `{YourGitHubUsername} submitted a pull request from feature/test-pr to main on {timestamp}`.

### Test 3: MERGE Action

1.  **Merge the PR**: On the Pull Request page in your `action-repo` on GitHub, click "Merge pull request" and confirm.
2.  **Verify**:
    * **GitHub**: Check webhook deliveries again; there should be another `pull_request` event, which your Flask application's logic will interpret as a MERGE.
    * **Flask Logs**: You should see logs indicating a "MERGE" event was processed.
    * **Your UI**: Your UI should update with a new entry like: `{YourGitHubUsername} merged branch feature/test-pr to main on {timestamp}`.

## Stopping the Project

To stop and remove the Docker containers:

```bash
docker stop <container-id> 

```

## Visuals & Demos

This section provides visual aids and links to demonstrate the project's functionality.

### Screenshots

<img width="1920" height="930" alt="Screenshot (473)" src="https://github.com/user-attachments/assets/ad424b45-0ffb-4a10-a4ea-0e66638a96e5" />
*Description: Screenshot of the UI before any GitHub events are processed.*

<img width="1920" height="906" alt="Screenshot (469)" src="https://github.com/user-attachments/assets/9a053989-34ca-4046-ad2f-802e7da6ce47" />
*Description: Screenshot of the UI displaying various GitHub events (Push, Pull Request, Merge).*

<img width="1920" height="901" alt="Screenshot (477)" src="https://github.com/user-attachments/assets/722bb509-bc6f-496a-816e-1577486e866c" />
*Description: Screenshot from GitHub showing a successful webhook delivery.*

### Video Demonstrations

**Project Demo (End-to-End Workflow)**

*Description: A video showcasing the full workflow from a Git action to UI update.*


### Important Links

Here are some important links related to the project.

* **`action-repo` on GitHub**: [https://github.com/YourGitHubUsername/action-repo](https://github.com/YourGitHubUsername/action-repo)
* **`webhook-repo` on GitHub**: [https://github.com/YourGitHubUsername/webhook-repo](https://github.com/YourGitHubUsername/webhook-repo)
* **MongoDB Documentation**: [https://docs.mongodb.com/](https://docs.mongodb.com/)
* **Flask Documentation**: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
* **GitHub Webhooks Documentation**: [https://docs.github.com/en/developers/webhooks-and-events/webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
* **ngrok**: [https://ngrok.com/](https://ngrok.com/)




