# Python based wet lab tank monitoring and control software

## Requirements:
  - gspread - https://github.com/burnash/gspread
  - oauth2client - https://github.com/googleapis/oauth2client
  - [Obtain OAuth2 credentials from Google Developers Console](http://gspread.readthedocs.org/en/latest/oauth2.html)

## Environment vars:
  - PROJECT_LOB_CONFIG - a path to the JSON config file
    - see sample_config.json

## Components and Sensors:
  - [DS18B20 waterproof temperature sensor](https://www.adafruit.com/product/381)
  - [water flow sensors](https://www.adafruit.com/product/828)
  - [solenoid valves](https://www.adafruit.com/product/997)
  - [eTape sensor](https://www.adafruit.com/product/3828)
  - Raspberry Pi

## To Run
### Hot Lobster Trial Monitoring

```sh
python -m project_lob.entrypoint -hm
```

or

```sh
python -m project_lob.entrypoint --hot-monitor
```

### Cold Lobster Trial Monitoring

```sh
python -m project_lob.entrypoint -cm
```

or

```sh
python -m project_lob.entrypoint --cold-monitor
```

Output is logged to _lobster_log.log_ in the current working dir
