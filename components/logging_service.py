import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
import time
import requests
import logging

class LoggingService(object):
    def __init__(self, sheet_key, cred_file,
            gmail_email, gmail_pwd, phone_numbers):
        self.logger = logging.getLogger(
            "project_lob.components.logging_service")
        self.logger.info("Initializing Logging Service")
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
        self.set_last_entry(time.time())
        self.connect()

    def set_last_entry(self, ts):
        self.logger.info("Setting last entry timestamp: {}".format(ts))
        self.last_entry_timestamp = ts

    def connect(self):
        self.logger.info("Connecting to google spreadsheets")
        self.connection = gspread.authorize(self.credentials)
        self.worksheet = self.connection.open_by_key(self.sh_key)
        self.sheet = self.worksheet.sheet1

    def connect_to_gmail_server(self):
        self.logger.info("Connecting to email server")
        self.g_server = smtplib.SMTP("smtp.gmail.com", 587)
        self.g_server.starttls()
        self.g_server.login(self.gmail_email, self.gmail_pwd)

    def disconnect_from_gmail(self):
        self.logger.info("Disconnecting from email server")
        self.g_server.quit()

    def send_multiple_texts(self, message, numbers):
        self.logger.info("Sending texts")
        self.connect_to_gmail_server()
        for phone in numbers:
            self.send_text_message(message, phone["number"], phone["carrier"])
        self.disconnect_from_gmail()

    def send_text_message(self, message, number, carrier = "ATT"):
        self.logger.info("Sending text to {}".format(number))
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
        self.logger.info("Checking Connection")
        if self.last_entry_timestamp and (time.time() -
                self.last_entry_timestamp > 1800):
            self.connect()
            self.set_last_entry(time.time())

    def add_entry(self, attrs, desired_row = None):
        self.logger.info("Adding entry")
        self.check_connection()
        try:
            current_row = desired_row or self.get_current_row()
            if current_row >= self.sheet.row_count:
                self.logger.info("Adding more rows to sheet")
                self.sheet.add_rows(5000)
            cells = self.sheet.range(current_row, 1, current_row, len(attrs))
            for i, n in enumerate(cells):
                cells[i].value = attrs[i]
            self.logger.info("Adding entry to row: {}".format(current_row))
            self.sheet.update_cells(cells)
        except (gspread.exceptions.APIError, requests.exceptions.ConnectionError) as e:
            self.logger.error("Error occured when adding entry: {}".format(e))
            if type(e) == gspread.exceptions.APIError:
                resp = requests.models.Response()
                resp._content = e.response.text.encode('latin-1')
                err = resp.json()
                code = "No Code"
                msg = "No Message"
                status = "No Status"
                if u'error' in err:
                    body = err[u'error']
                    if u'code' in body:
                        code = str(body[u'code'])
                    if u'message' in body:
                        msg = str(body[u'message'])
                    if u'status' in body:
                        status = str(body[u'status'])
                if status == "UNAUTHENTICATED":
                    self.logger.info("Error was UNAUTHENTICATED")
                    self.connect()
                    self.add_entry(attrs, current_row)
                elif code == "429":
                    self.logger.info("Error had code 429")
                    time.sleep(1)
                    self.add_entry(attrs, current_row)
                else:
                    self.logger.info("Error was unknown gspread error")
                    self.conect()
            else:
                self.logger.info("Unknown error")
                msg = "Unknown error"
                code = "Unknown Code"
                self.connect()
            self.send_multiple_texts(
                "Hot Lob Error! msg -> {} code -> {}".format(
                    msg.replace(":", ""),
                    code
                ),
                self.phone_numbers
            )
            self.error_count += 1
