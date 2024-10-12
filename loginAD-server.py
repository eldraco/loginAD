from flask import Flask, request, jsonify
import sqlite3
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename='app.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Database setup
def init_db():
    with sqlite3.connect('logins.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logins (
                id INTEGER PRIMARY KEY,
                server_ip TEXT NOT NULL,
                client_ip TEXT NOT NULL,
                login_time TEXT NOT NULL,
                username TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                connection_type TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/login', methods=['POST'])
def log_login():
    data = request.json
    logging.debug(f'Received data: {data}')
    try:
        with sqlite3.connect('logins.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO logins (server_ip, client_ip, login_time, username, success, connection_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (data['server_ip'], data['client_ip'], data['login_time'], data['username'], data['success'], data['connection_type']))
            conn.commit()
        logging.info("Login recorded successfully.")
        return jsonify({"message": "Login recorded.", "status": "success"}), 201
    except Exception as e:
        logging.error(f'Error recording login: {e}')
        return jsonify({"message": "Error recording login.", "status": "error"}), 500

if __name__ == '__main__':
    init_db()  # Initialize the database on startup
    app.run(host='0.0.0.0', port=5010)

