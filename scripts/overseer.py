import os
import json
import sys
import datetime
import logging
sys.path.append("../components")
from logging_service import LoggingService

if __name__ == '__main__':
	if "PROJECT_LOB_CONFIG" not in os.environ:
        print("PROJECT_LOB_CONFIG must be an environment variable set to "
	        "the path of a JSON config file.")
	    sys.exit()
	logger = logging.getLogger("project_lob.scripts.overseer")
	logger.info("Initializing overseer")
	config_path = os.environ["PROJECT_LOB_CONFIG"]
	with open(config_path) as f:
        config = json.load(f)["hot_lob"]
	with open(os.environ[config["phone_numbers"]]) as phones:
        phone_numbers = json.load(phones)
	service = LoggingService(
        os.environ[config["sheet_key"]],
        os.environ[config["cred_file"]],
        os.environ[config["gmail_email"]],
        os.environ[config["gmail_pwd"]],
	    phone_numbers,
	)
	while(true):
		logger.info("Fetching last entry")
        now = time.time()
        last_entry = service.get_last_entry()
        last_timestamp = time.mktime(time.strptime("{} {}".format(last_entry[0], last_entry[1])))
		logger.info("Last entry timestamp: {}".format(last_timestamp))
        if (now - last_timestamp) > 4200:
			logger.info("Sending alert message")
        	service.notify_all("Hot lob temperature monitor hasn't updated in over 70 minutes!")
		logger.info("Sleeping...")
        time.sleep(900)
