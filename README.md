# Python based wet lab tank monitoring and control software

## Requirements:
  - gspread - https://github.com/burnash/gspread
  - oauth2client - https://github.com/googleapis/oauth2client
  - [Obtain OAuth2 credentials from Google Developers Console](http://gspread.readthedocs.org/en/latest/oauth2.html)

## Environment vars:
  - HOT_LOBSTER_CRED_FILE - the credential file created when setting up gspread access
  - HOT_LOBSTER_SHEET_KEY - the google spreadsheet key found in the url for the desired spreadsheet
  - COLD_LOBSTER_CRED_FILE - use if different from HOT_LOBSTER_CRED_FILE
  - COLD_LOBSTER_SHEET_KEY - use if different from HOT_LOBSTER_SHEET_KEY
  - PROJECT_LOB_PHONES - a json file containing the phone numbers to send alerts to in the format of [{"number": "<phone_number>", "carrier": "ATT"}]
  - PROJECT_LOB_GMAIL_EMAIL - the email address to send text messages from
  - PROJECT_LOB_GMAIL_PWD   - the password to login with the email address above

## Components and Sensors:
  - [DS18B20 waterproof temperature sensor](https://www.adafruit.com/product/381)
  - [water flow sensors](https://www.adafruit.com/product/828)
  - [solenoid valves](https://www.adafruit.com/product/997)
  - [eTape sensor](https://www.adafruit.com/product/3828)
  - Raspberry Pi

## To Run
### Hot Lobster Trial Monitoring

```sh
python -m project_lob.scripts.monitor -hm
```

or

```sh
python -m project_lob.scripts.monitor --hot-monitor
```

### Cold Lobster Trial Monitoring

```sh
python -m project_lob.scripts.monitor -cm
```

or

```sh
python -m project_lob.scripts.monitor --cold-monitor
```

Output is logged to _lobster_log.log_ in the current working dir
