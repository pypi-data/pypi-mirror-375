import os, sys, yaml, json
import importlib.resources


class inputmodule:

    def __init__(self):
        default_file = importlib.resources.files('psqlmodule').joinpath('config.yaml')
        self.filename = os.environ.get('CONFIG_FILE', default_file)

    def get_data(self, filename=None, key=None):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            if filename is None:
                filename = self.filename
            else:
                self.filename = filename
            indata = None
            with open(filename, 'r') as fh:
                if not key:
                    indata = yaml.safe_load(fh)
                else:
                    d = yaml.safe_load(fh)
                    indata = d[f'{key}']
            ret_data['data'] = indata
        except Exception as e:
            err_msg = self.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            print(err_msg)
        return ret_data

    def err_format(self, err, api):
        _type, _obj, _trace = err
        _class = api
        _function = _trace.tb_frame.f_code.co_name
        _api = '%s.%s' % (_class, _function)
        _line = _trace.tb_lineno
        _file = _trace.tb_frame.f_code.co_filename
        try: _obj = json.loads(str(_obj))
        except: _obj = str(_obj)
        err_msg = {"error": _obj, "api": _api, "file": _file, "line": _line}
        return err_msg
