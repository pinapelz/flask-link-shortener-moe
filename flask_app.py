from flask import Flask, render_template, request, abort, jsonify, redirect
from database.sql_handler import SQLHandler
from flask_cors import CORS
import configparser
import string
import secrets
import os

app = Flask(__name__)
CORS(app)


parser = configparser.ConfigParser()
parser.read("config.ini")
CONFIG = parser

def create_database_connection():
    try:
        hostname = CONFIG.get("database", "host")
        user = CONFIG.get("database", "user")
        password = CONFIG.get("database", "password")
        database = CONFIG.get("database", "database")
        port = CONFIG.get("database", "port")
    except Exception:
        hostname = os.environ.get("MK_DATABASE_HOSTNAME")
        user = os.environ.get("MK_DATABASE_USER")
        password = os.environ.get("MK_DATABASE_PASSWORD")
        port = int(os.environ.get("MK_DATABASE_PORT"))
        database = os.environ.get("MK_DATABASE_NAME")
    return SQLHandler(host_name=hostname, username=user, password=password, database=database)



def initialize_database():
    sql_handler = create_database_connection()
    sql_handler.create_table(
        "shortened_links",
        "id INT AUTO_INCREMENT PRIMARY KEY, link VARCHAR(255), shortened_link VARCHAR(255) UNIQUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    )
    sql_handler.create_table(
        "authentication",
        "id INT AUTO_INCREMENT PRIMARY KEY, authkey VARCHAR(255) UNIQUE"
    )
initialize_database()


def generate_random_hash(length=6):
    characters = string.ascii_letters + string.digits
    random_hash = ''.join(secrets.choice(characters) for _ in range(length))
    return random_hash

@app.route('/')
def main_page():
    return render_template('index.html',
                           moe_image_url=CONFIG["site"]["moe_image"],
                           moe_quote=CONFIG["site"]["moe_quote"])

@app.route('/api/add_shortened', methods=['POST'])
def new_link():
    server = create_database_connection()
    requested_link = request.form.get("url")
    if requested_link is None:
        print("No link provided")
        return abort(400, "No link provided")
    if requested_link.strip() == "":
        return abort(400, "Cannot shorten empty link")
    if not requested_link.startswith("http://") and not requested_link.startswith("https://"):
        requested_link = "https://" + requested_link
    hash_value = generate_random_hash()

    while True:
        if server.check_row_exists("shortened_links", "shortened_link", hash_value):
            hash_value = generate_random_hash()
        else:
            break
    server.insert_row("shortened_links", "link, shortened_link", (requested_link, hash_value))
    server.close_connection()
    return jsonify(CONFIG["site"]["url"]+"/"+hash_value)

@app.route("/api/add_custom", methods=['POST'])
def add_custom():
    server = create_database_connection()
    requested_link = request.form.get("url")
    custom_link = request.form.get("custom")
    password = request.headers.get('X-AUTHENTICATION')
    if password is None:
        return abort(401, "Invalid Authentication")
    if not server.check_row_exists("authentication", "authkey", password):
        server.close_connection()
        return abort(401, "Invalid Authentication")

    if requested_link is None:
        print("No link provided")
        return abort(400, "No link provided")
    if requested_link.strip() == "":
        return abort(400, "Cannot shorten empty link")
    if not requested_link.startswith("http://") and not requested_link.startswith("https://"):
        requested_link = "https://" + requested_link
    if custom_link is None:
        return abort(400, "No custom link provided")
    if custom_link.strip() == "":
        return abort(400, "Cannot shorten empty link")
    if server.check_row_exists("shortened_links", "shortened_link", custom_link):
        server.close_connection()
        return abort(400, "Custom link already exists")
    server.insert_row("shortened_links", "link, shortened_link", (requested_link, custom_link))
    server.close_connection()
    return jsonify(CONFIG["site"]["url"]+"/"+custom_link)



@app.route('/<path>')
def expand_url(path):
    server = create_database_connection()
    if server.check_row_exists("shortened_links", "shortened_link", path):
        print("Link found")
        link = server.get_rows("shortened_links", "shortened_link", path)[0][1]
        print(link)
        server.close_connection()
        return redirect(link)
    server.close_connection()
    return abort(404, "Link not found")
    


if __name__ == '__main__':
    app.run(debug=True)
