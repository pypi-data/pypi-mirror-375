#!/usr/bin/python3
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from psqlmodule.inputmodule import *


class logger:
    i = inputmodule()

    def __init__(self):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self.i.get_data()
            if ret['status'] == 'failed':
                raise Exception(ret['err_msg'])

            data = ret['data']['logging']
            filename = data['log_file']
            maxBytes = data['file_size_mb'] * 1024 * 1024
            backupCount = data['backup_count']
            fmt = data['format']

            level = data['level']
            if level == 'DEBUG':
                level = logging.DEBUG
            elif level == 'INFO':
                level = logging.INFO
            elif level == 'WARN':
                level = logging.WARN
            elif level == 'ERROR':
                level = logging.ERROR
            elif level == 'CRITICAL':
                level = logging.CRITICAL

            dirname = os.path.dirname(filename)
            os.makedirs(dirname, exist_ok=True)
            rfh = RotatingFileHandler(
                filename=filename,
                mode='a',
                maxBytes=maxBytes,
                backupCount=backupCount,
                encoding=None,
                delay=0
            )
            logging.basicConfig(
                level=level,
                format=fmt,
                handlers=[
                    rfh,
                    logging.StreamHandler()
                ]
            )
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)


_logger = logger()
