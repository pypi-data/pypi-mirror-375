import psqlmodule.logger, logging
from psqlmodule.inputmodule import *
import sys

class GetSchema():
    i = inputmodule()

    def get_schema_name(self, tenant_id):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self.i.get_data()
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])

            # get schema prefix
            ret = self.get_schema_prefix()
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            schema_prefix = ret['data']

            schema = schema_prefix + '_' + str(tenant_id).replace('-','_')
            ret_data['data'] = schema
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data

    def get_schema_prefix(self):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self.i.get_data()
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            schema_prefix = os.getenv('TENANT_SCHEMA_PREFIX', ret['data']['schema']['prefix'])
            schema_prefix = schema_prefix.replace('-','_').rstrip('_')
            ret_data['data'] = schema_prefix
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data
