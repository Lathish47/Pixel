from flask import Flask, send_file, request
import datetime
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = 'your_spreadsheet_id'  # Replace with your Google Sheet ID
RANGE_NAME = 'Sheet1!A:D'  # Adjust the range as per your sheet structure

def get_google_sheets_service():
    creds = None
    with open('credentials.json') as source:
        creds = service_account.Credentials.from_service_account_info(
            json.load(source), scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

@app.route('/')
def home():
    return send_file("static/spy.gif", mimetype="image/gif")

@app.route('/image/<recipient_email>')
def spy_pixel(recipient_email):
    filename = "static/pixel.png"
    user_agent = request.headers.get('User-Agent')
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    get_ip = request.remote_addr

    data = '{"country_code":"Not found","country_name":"Not found","city":"Not found","postal":"Not found","latitude":"Not found","longitude":"Not found","IPv4":"IP Not found","state":"Not found"}'

    log_entry = [recipient_email, timestamp, user_agent, get_ip, data]

    try:
        service = get_google_sheets_service()
        sheet = service.spreadsheets()
        sheet.values().append(spreadsheetId=SPREADSHEET_ID,
                              range=RANGE_NAME,
                              valueInputOption='RAW',
                              insertDataOption='INSERT_ROWS',
                              body={'values': [log_entry]}).execute()
    except Exception as e:
        logging.error(f"Error writing to Google Sheets: {e}")
        return "Internal Server Error", 500

    return send_file(filename, mimetype="image/png")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
