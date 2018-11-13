Python based wet lab tank monitoring and control software

Requirements:
  - External Libraries:
    - gspread - https://github.com/burnash/gspread
    - oauth2client - https://github.com/googleapis/oauth2client

  - Environment:
    - HOT_LOBSTER_CRED_FILE - the credential file created when setting up gspread access
    - HOT_LOBSTER_SHEET_KEY - the google spreadsheet key found in the url for the desired spreadsheet
    - COLD_LOBSTER_CRED_FILE - (use if different from HOT_LOBSTER_CRED_FILE) the credential file created when setting up gspread access
    - COLD_LOBSTER_SHEET_KEY - (use if different from HOT_LOBSTER_SHEET_KEY) the google spreadsheet key found in the url for the desired spreadsheet
    - PROJECT_LOB_PHONES - a json file containing the phone numbers to send alerts to in the format of [{"number": "<phone_number>", "carrier": "ATT"}]
    - PROJECT_LOB_GMAIL_EMAIL - the email address to send text messages from
    - PROJECT_LOB_GMAIL_PWD   - the password to login with the email address above

  - Components:
    - DS18B20 waterproof temperature sensor - https://www.adafruit.com/product/381
    - water flow sensors - https://www.adafruit.com/product/828
    - solenoid valves    - https://www.adafruit.com/product/997
    - eTape sensor       - https://www.adafruit.com/product/3828
    - Raspberry Pi


To run:
  - follow the directions at https://github.com/burnash/gspread to set up the google spreadsheets authorization
  - ensure the environment variables above are set properly
  - python -m project_lob.scripts.monitor <arguments>
  - arguments:
    - --hot-monitor (-hm) to run the hot lobster trial montoring
    - --cold-monitor (-cm) to run the cold lobster trail monitoring

  - ex: python -m project_lob.scripts.monitor -hm
  - Output is logged to lobster_log.log at the working dir
