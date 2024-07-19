from flask import Flask, request, render_template, jsonify, redirect, url_for, send_file
import pandas as pd
import os
import csv
import sqlite3
from cleansing import cleanse_text

from flasgger import Swagger
from flasgger import swag_from

app = Flask(__name__, template_folder='templates')



# Swagger template with title, description, and version
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Text Cleansing API",  # Your desired title here
        "description": "A simple API for Cleansing Data Text",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": [
        "http"
    ]
}

# Configure Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "swagger_ui_url": "/docs",
    "specs_route": "/docs/"
}
swagger = Swagger(app, config=swagger_config, template=swagger_template)

#folder uplods and downloads
UPLOAD_FOLDER = 'uploads/'
DOWNLOAD_FOLDER = 'downloads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)


# Function to get base URL dynamically
def get_base_url():
    # Detect the current host and scheme (http or https)
    scheme = request.scheme
    host = request.host
    return f"{scheme}://{host}"

@app.route('/')
def index():
    return render_template('index.html')


#form imput
@app.route('/clean_text_form', methods=['POST'])
def clean_text_form_route():
    text = request.form.get('text')
    if not text:
        return render_template('result.html', error="No text provided"), 400

    cleaned_text = cleanse_text(text)

    conn = sqlite3.connect('database/clean_text.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO submissions (tweet, hs, abusive, hs_individual, hs_group, hs_religion, hs_race, hs_physical, hs_gender, hs_other, hs_weak, hs_moderate, hs_strong)
                      VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)''', (text,))
    submission_id = cursor.lastrowid
    cursor.execute('''INSERT INTO text_outputs (submission_id, tweet, hs, abusive, hs_individual, hs_group, hs_religion, hs_race, hs_physical, hs_gender, hs_other, hs_weak, hs_moderate, hs_strong)
                      VALUES (?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)''', (submission_id, cleaned_text))
    conn.commit()
    conn.close()

    return render_template('result.html', original_text=text, cleaned_text=cleaned_text)



#swagger imput
@app.route('/clean_text', methods=['POST'])
@swag_from("docs/swag-text.yml", methods=['POST'])
def clean_text_route():
    text = request.form.get('text') if 'text' in request.form else request.json.get('text')
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    cleaned_text = cleanse_text(text)

    conn = sqlite3.connect('database/clean_text.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO submissions (tweet, hs, abusive, hs_individual, hs_group, hs_religion, hs_race, hs_physical, hs_gender, hs_other, hs_weak, hs_moderate, hs_strong)
                      VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)''', (text,))
    submission_id = cursor.lastrowid
    cursor.execute('''INSERT INTO text_outputs (submission_id, tweet, hs, abusive, hs_individual, hs_group, hs_religion, hs_race, hs_physical, hs_gender, hs_other, hs_weak, hs_moderate, hs_strong)
                      VALUES (?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)''', (submission_id, cleaned_text))
    conn.commit()
    conn.close()

    # Check if the request is JSON (API call) or form submission (web)
    if request.is_json:
        return jsonify({"original_text": text, "cleaned_text": cleaned_text})
    else:
        return jsonify({"original_text": text, "cleaned_text": cleaned_text}) # Ensures JSON response even for form submissions








#form upload
@app.route('/upload_form', methods=['POST'])
def upload_file_form():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        cleansed_file_path = import_csv_to_db(file_path)
        return render_template('download.html', download_url=cleansed_file_path)
    return 'File upload failed'

def cleanse_tweet_form(tweet):
    cleansed_tweet = cleanse_text(tweet)
    return cleansed_tweet

def import_csv_to_db_form(file_path):
    conn = sqlite3.connect('database/clean_text.db')
    cursor = conn.cursor()
    cleansed_data = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        for row in csv_reader:
            cursor.execute('''INSERT INTO submissions (tweet, hs, abusive, hs_individual, hs_group, hs_religion, hs_race, hs_physical, hs_gender, hs_other, hs_weak, hs_moderate, hs_strong)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', row)
            submission_id = cursor.lastrowid
            cleansed_tweet = cleanse_tweet(row[0])
            cleansed_row = [cleansed_tweet] + row[1:]
            cleansed_data.append([submission_id] + cleansed_row)
            cursor.execute('''INSERT INTO text_outputs (submission_id, tweet, hs, abusive, hs_individual, hs_group, hs_religion, hs_race, hs_physical, hs_gender, hs_other, hs_weak, hs_moderate, hs_strong)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', [submission_id] + cleansed_row)
    conn.commit()
    conn.close()

    cleansed_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], os.path.basename(file_path))
    with open(cleansed_file_path, 'w', newline='', encoding='utf-8') as cleansed_file:
        csv_writer = csv.writer(cleansed_file)
        csv_writer.writerow(headers)
        for row in cleansed_data:
            csv_writer.writerow(row[1:])
    return cleansed_file_path





#swagger upload
@app.route('/upload', methods=['POST'])
@swag_from("docs/swag-upload.yml", methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        cleansed_file_path = import_csv_to_db(file_path)

        base_url = get_base_url()
        
        download_url = f"{base_url}{url_for('download_file', filename=cleansed_file_path)}"

        return jsonify({"message": "File uploaded and processed successfully", "download_url": download_url })
    return jsonify({"error": "File upload failed"}), 500

def cleanse_tweet(tweet):
    cleansed_tweet = cleanse_text(tweet)
    return cleansed_tweet

def import_csv_to_db(file_path):
    conn = sqlite3.connect('database/clean_text.db')
    cursor = conn.cursor()
    cleansed_data = []
    # with open(file_path, 'r', encoding='utf-8') as file:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:

        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        for row in csv_reader:
            cursor.execute('''INSERT INTO submissions (tweet, hs, abusive, hs_individual, hs_group, hs_religion, hs_race, hs_physical, hs_gender, hs_other, hs_weak, hs_moderate, hs_strong)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', row)
            submission_id = cursor.lastrowid
            cleansed_tweet = cleanse_tweet(row[0])
            cleansed_row = [cleansed_tweet] + row[1:]
            cleansed_data.append([submission_id] + cleansed_row)
            cursor.execute('''INSERT INTO text_outputs (submission_id, tweet, hs, abusive, hs_individual, hs_group, hs_religion, hs_race, hs_physical, hs_gender, hs_other, hs_weak, hs_moderate, hs_strong)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', [submission_id] + cleansed_row)
    conn.commit()
    conn.close()

    cleansed_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], os.path.basename(file_path))
    with open(cleansed_file_path, 'w', newline='', encoding='utf-8') as cleansed_file:
        csv_writer = csv.writer(cleansed_file)
        csv_writer.writerow(headers)
        for row in cleansed_data:
            csv_writer.writerow(row[1:])
    return cleansed_file_path



#download
@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_file(filename, as_attachment=True)


##404 page 
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
