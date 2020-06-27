import logging
from logging.handlers import RotatingFileHandler

logformatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
logFile = './alteration.log'
handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, 
                                    backupCount=2, encoding=None, delay=0)
handler.setFormatter(logformatter)
handler.setLevel(logging.INFO)
alterationlog = logging.getLogger('root')
alterationlog.setLevel(logging.INFO)
alterationlog.addHandler(handler)