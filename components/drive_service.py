import gspread
from oauth2client.service_account import ServiceAccountCredentials

class DriveService(object):
    def __init__(self, sheet_key, cred_file):
        self.sh_key = sheet_key
        self.cred_file = cred_file
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        self.connect()

    def connect(self):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.cred_file,
            self.scope
        )
        self.connection = gspread.authorize(self.credentials)
        self.worksheet = gc.open_by_key(self.sh_key)
        self.sheet = self.worksheet.sheet1

    def get_current_row(self):
        if not self.sheet:
            raise Exception("Cannot get current row without a sheet. Please run the connect function to setup the worksheet")
        return len(self.sheet.col_values(1)) + 1

    def add_entry(self, attrs):
        current_row = self.get_current_row()
        for i, n in enumerate(attrs):
            self.sheet.update_cell(current_row, (i + 1), n)
