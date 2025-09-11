from copy import deepcopy
from psqlmodule.inputmodule import *
import psqlmodule.logger, logging
import os, re
from psqlmodule.text_color import TextColor
tc = TextColor()

class find_levelled_master_table_list():
    """
    This class is used to find the master table list from a given dict of key-value pairs of table vs master_table
    (connected with foreign key)

    Note: the key value pair of table -- mastertable can be generated from the following sql query (out of scope of this class)

    SELECT tc.table_name AS source_table, ccu.table_name AS target_table FROM information_schema.table_constraints AS tc JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name JOIN information_schema.constraint_column_usage AS ccu ON tc.constraint_name = ccu.constraint_name WHERE tc.constraint_type = 'FOREIGN KEY'

    """
    i = inputmodule()

    def __init__(self):
        try:
            #use_envs = True if re.search('true', str(os.getenv('USE_ENVS')), re.M|re.I) else False
            use_envs = True
            if use_envs:
                self.loop_check = 100
            else:
                ret = self.i.get_data()
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                self.loop_check = ret['data']['consumer']['loop_check']

        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)


    # obsolete
    def find_levelled_master_table_list(self, table_dict):
        levelled_master_table_list = self.recursive_find_master_table_list(table_dict)
        _tables_to_be_excluded = []
        for i in levelled_master_table_list: _tables_to_be_excluded += i
        _keys_to_add = [k for k in table_dict if k not in _tables_to_be_excluded]
        levelled_master_table_list.append(_keys_to_add)
        levelled_master_table_list = [k for k in levelled_master_table_list if k]
        return levelled_master_table_list
    
    
    # obsolete
    def recursive_find_master_table_list(self, table_dict):
        levelled_master_table_list = []
        _level_list = self.find_master_table_list(table_dict)
        levelled_master_table_list.append(_level_list)
        _to_remove = [k for k,v in zip(table_dict.keys(),table_dict.values()) if v in _level_list]
        _t_dict = deepcopy(table_dict)
        [_t_dict.pop(k) for k in _to_remove]
        if _t_dict:
            levelled_master_table_list += self.recursive_find_master_table_list(_t_dict)
        return levelled_master_table_list
    
    
    # obsolete
    def find_master_table_list(self, table_dict):
        master_table_list = []
        for table in table_dict:
            m_table = self.find_master_table(table_dict, table)
            master_table_list.append(m_table)
        master_table_list = list(set(master_table_list))
        return master_table_list
    
    
    # obsolete
    def find_master_table(self, table_dict, table):
        master_table = table_dict[table]
        if master_table in table_dict:
           master_table = self.find_master_table(table_dict, master_table)
        return master_table


    # latest where one table can have fk relation to multiple tables
    def _get_table_vs_master_table_dict(self, data):
        """
        This API will convert a list of tuples to a dict of table(key) with one or more fk relational tables(list)
        {'table': ['fk_table1', 'fk_table2', 'fk_table3']}
        It will also add master tables as keys in the dict with empty values,
        this is needed when we have to recurrsively remove the master tables from tables dict in the next step
        """ 
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            d = {}
            master_tables = []
            for k,v in data:
                l = []
                l.append(v)
                for i,j in data:
                    if i == k and j not in l:
                        l.append(j)
                d[k] = l
            data = d
            j = [[r for r in i if r not in data.keys()] for i in data.values()]
            [[master_tables.append(k) for k in l] for l in j]
            master_tables = list(set(master_tables))
            d = {k:[] for k in master_tables}
            data.update(d)
            ret_data['data'] = data
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _get_next_master_table_list(self, data):
        """
        This API will get next list of master tables
        It will do so by first removing any keys from the dict with empty value list
        and then removes those master tables from the values of each keys
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            # get master tables list
            master_tables = [k for k in data if len(data[k]) == 0]
            # remove master tables from keys
            [data.pop(k) for k in master_tables]
            # remove master tables from values if any
            [[data[k].remove(i) for i in master_tables if i in data[k]] for k in data]
            ret_data['data'] = master_tables
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data

 
    def fetch_levelled_master_table_list(self, data):
        """
        This API will get list of master tables level by level
        so that the dict shrinks step by step giving list of master tables at each step
        ultimately the dict is empty and we have a level wise list of list of master tables
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            # first get a table dict from a list of tuples data type
            ret = self._get_table_vs_master_table_dict(data=data)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            table_dict = ret['data']
        
            # keep a check on loop 
            loop_check=0

            # initialize levelled list 
            levelled_list = []
            while table_dict:
                ret = self._get_next_master_table_list(data=table_dict)
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                levelled_list.append(ret['data'])
                loop_check+=1
                if loop_check >= self.loop_check:
                    i = 0
                    levelled_list = [k for k in levelled_list if k]
                    for level in levelled_list:
                        i+=1
                        msg = f'Level-{i}: %s' %level
                        #logging.warning('\n\n\t%s%s%s%s\n' %(tc.bg_yellow,tc.blue,msg,tc.reset))
                    #logging.warning('%s%s%s%s' %(tc.bg_yellow,tc.blue,f'UNUSUAL LOOP DETECTED IN FOREIGN KEY RELATIONS BETWEEN TABLES, LOOP LEVEL: {self.loop_check}',tc.reset))
                    break
                    # raise Exception('UNUSUAL LOOP DETECTED IN FOREIGN KEY RELATIONS BETWEEN TABLES, LOOP LEVEL: %s' %self.loop_check)
            ret_data['data'] = levelled_list
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error('%s%s%s%s' %(tc.bg_red,tc.white,err_msg,tc.reset))
        return ret_data

 
if __name__ == '__main__':
    pass
