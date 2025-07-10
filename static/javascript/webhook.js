// static/js/scripts.js

const eventsDisplay = document.getElementById('events-display');


// When deploying, this should be your domain, e.g., "https://your-domain.com/events"

const API_URL = "https://a5169b202608.ngrok-free.app/events"; // Replace with your Flask app's public URL


async function fetchAndDisplayEvents() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const events = await response.json();
        renderEvents(events);
    } catch (error) {
        console.error("Could not fetch events:", error);
        eventsDisplay.innerHTML = "<p>Error loading events. Please ensure the backend is running and accessible.</p>";
    }
}

function renderEvents(events) {
    if (events.length === 0) {
        eventsDisplay.innerHTML = "<p>No events recorded yet. Push some changes to your GitHub repo to see activity!</p>";
        return;
    }
    eventsDisplay.innerHTML = "";
    events.forEach(event => {
        let eventMessage = "";
        let actionClass = "action-default"; // Default class for unhandled actions

        // Ensure timestamp is a valid date string/number
        const timestamp = new Date(event.timestamp).toLocaleString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric',
            hour: '2-digit', minute: '2-digit', hour12: true,
            timeZoneName: 'short'
        });

        switch (event.action) {
            case "PUSH":
                eventMessage = `<span class="${actionClass}">PUSH:</span> ${event.author} pushed to <b>${event.to_branch}</b> on ${timestamp}`;
                actionClass = "action-push";
                break;
            case "PULL_REQUEST":
                eventMessage = `<span class="${actionClass}">PULL REQUEST:</span> ${event.author} submitted pull request #${event.pull_request_id} titled "<b>${event.title}</b>" from <b>${event.from_branch}</b> to <b>${event.to_branch}</b> on ${timestamp}`;
                actionClass = "action-pull-request";
                break;
            case "MERGE":
                eventMessage = `<span class="${actionClass}">MERGE:</span> ${event.author} merged pull request #${event.pull_request_id} from <b>${event.from_branch}</b> into <b>${event.to_branch}</b> on ${timestamp}`;
                actionClass = "action-merge";
                break;
            case "PULL_REQUEST_CLOSED": 
                eventMessage = `<span class="${actionClass}">PR CLOSED:</span> ${event.author} closed pull request #${event.pull_request_id} titled "<b>${event.title}</b>" (unmerged) on ${timestamp}`;
                actionClass = "action-pull-request"; // Use same color as PR
                break;
            default:
                eventMessage = `<span class="${actionClass}">UNKNOWN ACTION:</span> <b>${event.action}</b> by ${event.author} on ${timestamp}`;
                actionClass = "action-default";
        }

        const eventItem = document.createElement('div');
        eventItem.classList.add('event-item');
        

        eventItem.innerHTML = `
            <p>${eventMessage}</p>
            <p class="timestamp">Repo: ${event.repository || 'N/A'} | Request ID: ${event.request_id}</p>
        `;
        eventsDisplay.appendChild(eventItem);
    });
}

// Fetch immediately on load
fetchAndDisplayEvents();

// Poll every 15 seconds
setInterval(fetchAndDisplayEvents, 15000);