
from flask import request, jsonify, render_template
from datetime import datetime

#setup_routes function executes the routes and this function parameters are passed from app.py
def setup_routes(app_flask, events_collection):
    
    
    
    @app_flask.route('/webhook', methods=['POST'])
    def github_webhook():
        event = request.headers.get('X-GitHub-Event')            #stores the Event type like push,pull request, merge
        payload = request.get_json()                             #This payload stores the info about a request of github webhooks to work

        data_to_store = {}                                       #stores the informations of push events etc....
        data_to_store["timestamp"] = datetime.utcnow().isoformat() + "Z" # UTC format

        if event == 'push':
            data_to_store["action"] = "PUSH"
            data_to_store["author"] = payload['pusher']['name']
            data_to_store["from_branch"] = payload['base_ref'] if 'base_ref' in payload and payload['base_ref'] else "N/A" # Push doesn't always have a clear from_branch
            data_to_store["to_branch"] = payload['ref'].split('/')[-1]
            data_to_store["request_id"] = payload['after'] 
            data_to_store["repository"] = payload['repository']['full_name']
            
        elif event == 'pull_request':
            action_type = payload['action']
            
            if action_type == 'opened':
                data_to_store["action"] = "PULL_REQUEST"
                data_to_store["author"] = payload['pull_request']['user']['login']
                data_to_store["from_branch"] = payload['pull_request']['head']['ref']
                data_to_store["to_branch"] = payload['pull_request']['base']['ref']
                data_to_store["request_id"] = str(payload['pull_request']['id'])
                
            elif action_type == 'closed' and payload['pull_request']['merged']:
                # This handles the merge action if it's part of a PR close
                data_to_store["action"] = "MERGE"
                data_to_store["author"] = payload['pull_request']['merged_by']['login']
                data_to_store["from_branch"] = payload['pull_request']['head']['ref']
                data_to_store["to_branch"] = payload['pull_request']['base']['ref']
                data_to_store["request_id"] = str(payload['pull_request']['id'])
                
            else:
                return jsonify({"message": f"Unhandled pull request action: {action_type}"}), 200
            
        elif event == 'create' and payload['ref_type'] == 'branch':
            pass # 
        
        else:
            return jsonify({"message": f"Unhandled event: {event}"}), 200

        if data_to_store and "action" in data_to_store:    #stored data is added to mongo database using collections
            events_collection.insert_one(data_to_store) 
            
            return jsonify({"status": "success", "message": "Event received and stored"}), 200
        else:
            return jsonify({"message": "No relevant data to store for this event"}), 200

    @app_flask.route('/events', methods=['GET'])
    def get_events():
        latest_events = list(events_collection.find().sort("timestamp", -1).limit(20)) # Use the passed collection
        for event in latest_events:
            event['_id'] = str(event['_id'])
        return jsonify(latest_events), 200

    @app_flask.route('/')
    def index():
        latest_events = list(events_collection.find().sort("timestamp", -1).limit(20)) # Use the passed collection
        return render_template('UI.html', events=latest_events)


