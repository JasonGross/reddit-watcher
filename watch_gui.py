#!/usr/bin/env python3
if __name__ == '__main__':
    try:
        import logging
        import time
        import watch
        import watch_config
        import watch_version

        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.INFO,
                            datefmt="%H:%M:%S")
        logging.info(f'Using configuration file {watch_config.CONF_FILE}, CONFIG_VERSION: {watch_config.CONFIG_VERSION}')
        logging.info(f'Program version {watch_version.MAJOR}.{watch_version.MINOR}.{watch_version.REVISION}')
        watch_config.load_configuration()
        time.sleep(10)
        while True:
            watch.refresh_sleep_console()
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        logging.critical(f'Encountered an error:\n{e}')
        input('Press ENTER to exit...')
        raise e
