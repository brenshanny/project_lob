import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
import time
import requests

class LobsterLog(object):
    def __init__(self, sheet_key, cred_file,
            gmail_email, gmail_pwd, phone_numbers):
        self.sh_key = sheet_key
        self.cred_file = cred_file
        self.gmail_email = gmail_email
        self.gmail_pwd = gmail_pwd
        self.phone_numbers = phone_numbers
        self.error_count = 0
        self.connect_to_gmail_server()
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.cred_file,
            self.scope
        )
        self.last_entry_timestamp = time.time()
        self.connect()

    def connect(self):
        self.connection = gspread.authorize(self.credentials)
        self.worksheet = self.connection.open_by_key(self.sh_key)
        self.sheet = self.worksheet.sheet1

    def connect_to_gmail_server(self):
        self.g_server = smtplib.SMTP("smtp.gmail.com", 587)
        self.g_server.starttls()
        self.g_server.login(self.gmail_email, self.gmail_pwd)

    def disconnect_from_gmail(self):
        self.g_server.quit()

    def send_multiple_texts(message, numbers):
        self.connect_to_gmail_server()
        for phone in numbers:
            self.send_text_message(message, phone["number"], phone["carrier"])
        self.disconnect_from_gmail()

    def send_text_message(message, number, carrier = "ATT"):
        addr = "@mms.att.net"
        if carrier == "Verizon":
            addr = "@verizon.net"
        elif carrier == "TMoblie":
            addr = "@tmomail.net"
        self.g_server.sendmail(
            self.gmail_email,
            "{}{}".format(number, addr),
            message
        )

    def get_current_row(self):
        self.check_connection()
        if not self.sheet:
            raise Exception("Cannot get current row without a sheet."
            "Please run the connect function to setup the worksheet"
        )
        return len(self.sheet.col_values(1)) + 1

    def check_connection(self):
        if self.last_entry_timestamp and (time.time() -
                self.last_entry_timestamp > 18000):
            self.connect()

    def add_entry(self, attrs, desired_row = None):
        self.check_connection()
        try:
            current_row = desired_row or self.get_current_row()
            cells = self.sheet.range(current_row, 1, current_row, len(attrs))
            for i, n in enumerate(cells):
                cells[i].value = attrs[i]
            self.sheet.update_cells(cells)
        except (gspread.exceptions.APIError, requests.exceptions.ConnectionError) as e:
            self.send_multiple_texts(
                "There was an error: {}".format(e.message),
                self.phone_numbers
            )
            self.error_count += 1
            if e.status == "UNAUTHENTICATED":
                print("Error: {}".format(e.status))
                self.connect()
                self.add_entry(attrs, current_row)
            elif e.code == 429:
                print("Error: Too many requests")
                time.sleep(1)
                self.add_entry(attrs, current_row)
            else:
                self.connect()
