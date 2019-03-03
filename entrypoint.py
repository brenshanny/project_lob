import os
import logging
import argparse
import sys

from .controllers.temperature_only_monitor import TemperatureOnlyMonitor
from .controllers.cold_lobs import ColdLobMonitor

if __name__ == "__main__":
    # Check for config file
    if "PROJECT_LOB_CONFIG" not in os.environ:
        print("PROJECT_LOB_CONFIG must be an environment variable set to "
              "the path of a JSON config file.")
        sys.exit()
    config_path = os.environ["PROJECT_LOB_CONFIG"]

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-hm", "--hot-monitor", help="Run the hot lob monitor",
                         action="store_true")
    parser.add_argument("-cm", "--cold-monitor", help="Run the cold lob monitor",
                         action="store_true")
    parser.add_argument("-cmt", "--cold-monitor-temp", help="Run the cold monitor with temperature readings only",
                         action="store_true")
    args = parser.parse_args()
    if not args.hot_monitor and not args.cold_monitor and not args.cold_monitor_temp:
        print("Must specify a program to run, hot monitor or cold"
              " controller!")
        sys.exit()
    if args.hot_monitor and args.cold_monitor:
        print("Cannot run both hot and cold monitoring programs."
              " Please specify one")
        sys.exit()

    # Setup logging
    logger = logging.getLogger('project_lob')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('lobster_log.log')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    # Run monitor
    if args.hot_monitor:
        logger.info("Creating hot lob monitor!")
        monitor = TemperatureOnlyMonitor(config_path, "hot_lob")
    if args.cold_monitor:
        logger.info("Creating cold lob monitor!")
        monitor = ColdLobMonitor(config_path)
    if args.cold_monitor_temp:
        logger.info("Creating cold lob temp only monitor!")
        monitor = TemperatureOnlyMonitor(config_path, "cold_lob_temp")
    monitor.run()
