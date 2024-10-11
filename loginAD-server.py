import argparse
import logging
import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime

# Initialize Flask application
app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:%(message)s')

# Database setup
def init_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logins (
            id INTEGER PRIMARY KEY,
            server_ip TEXT NOT NULL,
            client_ip TEXT NOT NULL,
            login_time TEXT NOT NULL,
            username TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# API endpoint to receive login data
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        server_ip = data['server_ip']
        client_ip = data['client_ip']
        login_time = data['login_time']
        username = data['username']

        # Store the data in the SQLite database
        conn = sqlite3.connect('logins.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO logins (server_ip, client_ip, login_time, username)
            VALUES (?, ?, ?, ?)
        ''', (server_ip, client_ip, login_time, username))
        conn.commit()
        conn.close()

        logging.info(f'Login recorded: {server_ip}, {client_ip}, {login_time}, {username}')
        return jsonify({'status': 'success', 'message': 'Login recorded.'}), 201

    except Exception as e:
        logging.error(f'Error recording login: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 400

# Main function to run the server
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Login Anomaly Detection API')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()

    # Initialize the database
    init_db('logins.db')

    # Run the Flask app
    app.run(host='0.0.0.0', port=args.port)
