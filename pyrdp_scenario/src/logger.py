import logging
import json
import sys

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'message': record.getMessage(),
        }
        return json.dumps(log_data)

class JsonConsoleHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        logging.StreamHandler.__init__(self, stream)

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg)
            stream.write("\n")
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)