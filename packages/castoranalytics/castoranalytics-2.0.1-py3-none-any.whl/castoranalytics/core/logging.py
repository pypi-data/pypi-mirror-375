import sys
import datetime


class LogManager:
    def __init__(self):
        self._name = 'castormobile'

    def _log(self, level, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f'[{timestamp}] {level} {self._name}: {message}'
        if hasattr(sys, '_MEIPASS'):
            with open('CastorAnalytics.log', 'w', encoding='utf-8') as f:
                f.write(message + '\n')
        print(message)

    def info(self, message):
        self._log('INFO', message)

    def warning(self, message):
        self._log('WARNING', message)

    def error(self, message):
        self._log('ERROR', message)