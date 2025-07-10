from flask import Flask
from dotenv import load_dotenv

#Imported the Database from database file and relevant values 
from database import client, events_collection, db



load_dotenv()

app = Flask(__name__)

#Imported the routes file and methods  to invoke the function passing the database parameters to it 
from routes import setup_routes           
setup_routes(app, events_collection)


if __name__ == '__main__':
    
    
    try:                                        #To check the MongoDB connection working or not
        
        client.admin.command('ismaster')
        print("MongoDB connection successful.")
        
    except Exception as e:
        
        print(f"Failed to connect to MongoDB: {e}")
        print("Please ensure MongoDB is running and accessible at the specified URI.")
       
        exit(1)
    
    
    app.run(host='0.0.0.0', port=5000, debug=True)