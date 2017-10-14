#!/usr/bin/env python

import os
import sys
import logging
import logging.config

from home_tv_controller.app import App


def main():
    logging.config.fileConfig(os.path.join(os.path.dirname(__file__), '..', 'logging.conf'))
    logger = logging.getLogger()
    logger.info('Booted')
    app = App()
    app.connect_mqtt()
    app.run_forever()


if __name__ == '__main__':
    main()
