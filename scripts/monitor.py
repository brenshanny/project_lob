import os
import logging
import argparse
import sys

from ..controllers.hot_lobs import HotLobMonitor
from ..controllers.cold_lobs import ColdLobMonitor

if __name__ == "__main__":
    logger = logging.getLogger('project_lob')
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler('lobster_log.log')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    parser = argparse.ArgumentParser()
    parser.add_argument("-hm", "--hot-monitor", help="Run the hot lob monitor",
                         action="store_true")
    parser.add_argument("-cm", "--cold-monitor", help="Run the cold lob monitor",
                         action="store_true")
    args = parser.parse_args()
    if not args.hot_monitor and not args.cold_monitor:
        print("Must specify a program to run, hot monitor or cold"
              " controller!")
        sys.exit()
    if args.hot_monitor and args.cold_monitor:
        print("Cannot run both hot and cold monitoring programs."
              " Please specify one")
        sys.exit()
    if args.hot_monitor:
        logger.info("Creating hot lob monitor!")
        config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'hot_lobs_config.json')
        monitor = HotLobMonitor(config_path)
    if args.cold_monitor:
        logger.info("Creating cold lob monitor!")
        config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'cold_lobs_config.json')
        monitor = ColdLobMonitor(config_path)
    monitor.run()