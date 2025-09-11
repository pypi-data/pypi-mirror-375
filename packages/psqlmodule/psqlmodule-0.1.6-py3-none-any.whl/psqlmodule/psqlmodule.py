import os, sys, re, json
import psycopg
import psqlmodule.logger, logging
from psqlmodule.inputmodule import *
from copy import deepcopy
from datetime import datetime, timedelta
import binascii, time
import base64
import pandas as pd
import numpy as np
from psqlmodule.find_levelled_master_table_list import *
from tqdm import tqdm


class psqlmodule():
    """
        pslmodule
        To connect to the database
        Add the following envs:

            POSTGRES_HOST=<database ip>
            POSTGRES_PORT=<database port>
            POSTGRES_USER=<db username>
            POSTGRES_DB=<db name>
            POSTGRES_PASSWORD=<db password>

        OR
        Set the following variables:

            p.db = <database>
            p.host = <host>
            p.user = <user>
            p.password = <password>
            p.port = <port>
            p._connect()
    """
    i = inputmodule()
    f = find_levelled_master_table_list()
    connection_less = True


    def __init__(self):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            #use_envs = True if re.search('true', str(os.getenv('USE_ENVS')), re.M|re.I) else False
            use_envs = True
            if use_envs:
                self.host = os.getenv('POSTGRES_HOST')
                self.port = int(os.getenv('POSTGRES_PORT', '5432'))
                self.user = os.getenv('POSTGRES_USER')
                self.db = os.getenv('POSTGRES_DB')
                self.password = os.getenv('POSTGRES_PASSWORD')
            else:
                ret = self.i.get_data()
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                self.psqlData = ret['data']['targetdb']
                sql_data = self.psqlData
                self.host = sql_data['host']
                self.port = sql_data['port']
                self.user = sql_data['user']
                self.db = sql_data['database']
                ret = self.c.decrypt(sql_data['password'])
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                self.password = ret['data']
            #ret = self.setup_database()
            #if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            # logging.debug('Initialized "psqlmodule" successfully')
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)


    def _connect(self, host=None, port=None, user=None, password=None, db=None):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            if self.connection_less:
                if host == None: host = self.host
                if port == None: port = self.port
                if user == None: user = self.user
                if password == None: password = self.password
                if db == None: db = self.db
                #self.connection = psycopg.connect(host=host, port=port, user=user, password=password, database=db)
                self.connection = psycopg.connect(host=host, port=port, user=user, password=password, dbname=db)
                self.mycursor = self.connection.cursor()
                # logging.debug('Connected to postgresql database server: "%s" successfully' %host)
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _connect_raw(self, host=None, port=None, user=None, password=None, db=None):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            if self.connection_less:
                if host == None: host = self.host
                if port == None: port = self.port
                if user == None: user = self.user
                if password == None: password = self.password
                self.connection = psycopg.connect(host=host, port=port, user=user, password=password)
                self.mycursor = self.connection.cursor()
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _convert_int_to_date(self, dateint):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            reference_date = datetime(1970, 1, 1)
            result_date = reference_date + timedelta(days=dateint)
            ret_data['data'] = result_date
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _convert_int_to_timestamp(self, micro_timestamp):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            try:
                ts = int(micro_timestamp)
                timestamp = ts / 1000000
                result_time = datetime.fromtimestamp(timestamp)
                ret_data['data'] = result_time
            except:
                ret_data['data'] = micro_timestamp
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def format_seconds(self, seconds):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            td = timedelta(seconds=seconds)
            hours, remainder = divmod(td.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            ret_data['data'] = f"{hours:02d}H:{minutes:02d}m:{seconds:02d}s"
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _convert_base64_to_hex(self, b64str):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            hex_data = binascii.hexlify(base64.b64decode(b64str)).upper().decode('utf-8')
            ret_data['data'] = hex_data
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _convert_bytes_to_hex(self, byteStr):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            hex_data = bytes.hex(byteStr).upper()
            ret_data['data'] = hex_data
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _convert_hex_to_base64(self, hexstr):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            b64str = base64.b64encode(binascii.unhexlify(hexstr))
            ret_data['data'] = b64str
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _disconnect(self):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            if self.connection_less:
                self.mycursor.close()
                self.connection.close()
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _select_database(self, db):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            self.mycursor.execute(query='\\c %s' %(db,))
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def commit(self):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            self.connection.commit()
            # logging.debug('Committed changes to database')
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def get_databases(self):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            databases = []
            ret = self._connect()
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            self.mycursor.execute('SELECT DATNAME from pg_database')
            for d in self.mycursor:
                d, = d
                databases.append(d)
            # logging.debug('Getting database info')
            ret_data['data'] = databases
            self._disconnect()
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self._disconnect()
        return ret_data

 
    def isdatabase_exists(self, db, disp=False):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            db_exists = False
            ret = self._connect_raw()
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            self.mycursor.execute('SELECT DATNAME from pg_database')
            for d in self.mycursor:
                if db in d:
                    d, = d
                    db_exists = True
            ret_data['data'] = db_exists
            if disp:
                logging.debug('Database "%s" exists? : %s' %(db, 'exists' if db_exists else 'doesn\'t exist'))
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self._disconnect()
        return ret_data


    def get_tables(self, db=None, schema='public'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            tables = []
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            # self.mycursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            self.mycursor.execute(query="SELECT table_name FROM information_schema.tables WHERE table_schema = '%s' AND table_type = 'BASE TABLE' AND table_name <> 'spatial_ref_sys'" %(schema,))
            for t in self.mycursor:
                t, = t
                tables.append(t)
            ret_data['data'] = tables
            # logging.debug('Getting database tables')
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self._disconnect()
        return ret_data


    def istable_exists(self, db, table, schema='public', disp=False):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            table_exists = False
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            self.mycursor.execute(query="SELECT table_name FROM information_schema.tables WHERE table_schema = '%s'" %(schema,))
            for t in self.mycursor:
                if table in t:
                    t, = t
                    table_exists = True
            ret_data['data'] = table_exists
            if disp:
                logging.debug('Table "%s" exists? : %s' %(table, 'exists' if table_exists else 'doesn\'t exist'))
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self._disconnect()
        return ret_data


    def describe_table(self, db, table, schema='public'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            self.mycursor.execute(query='SELECT * from %s."%s" LIMIT 0' %(schema,table))
            table_info = self.mycursor.description
            self.mycursor.execute(query='SELECT oid,typname FROM pg_type')
            pg_types = self.mycursor.fetchall()
            pg_type_dict = {}
            [pg_type_dict.update({i[0]:i[1]}) for i in pg_types]
            table_description = {}
            [table_description.update({tinfo.name: pg_type_dict[tinfo.type_code]}) for tinfo in table_info]
            ret_data['data'] = table_description
            # logging.debug('Describe table : "%s"' %table)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def insert_rows(self, db, table, columns, values, schema='public'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.lock_table(db=db, table=table, schema=schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            sql = "INSERT INTO %s.%s %s VALUES %s"
            self.mycursor.execute(query=sql %(schema, table, columns, values))
            ret = self.commit()
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            # logging.debug('Inserted rows into : %s' %table)
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def get_table(self, db, table, schema='public', disp=False, query='*', where='', raw_query=''):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            # Fetch Column Names & Types
            ret = self.describe_table(db=db, table=table, schema=schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            columns_info = ret['data']

            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.lock_table(db=db, table=table, schema=schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            if where == '':
                self.mycursor.execute(query='SELECT %s FROM %s."%s" %s' %(query, schema, table, raw_query))
            else:
                self.mycursor.execute(query='SELECT %s FROM %s."%s" WHERE %s %s' %(query, schema, table, where, raw_query))

            # Process data in chunks
            chunks = []
            batch_size = 1000
            while True:
                rows = self.mycursor.fetchmany(batch_size)

                if not rows and len(chunks) > 0:
                    break

                df_chunk = pd.DataFrame(rows, columns=columns_info.keys())
                for col, dtype in columns_info.items():
                    if dtype in ("integer", "bigint", "smallint"):
                        df_chunk[col] = [str(int(k)) if pd.notna(k) else k for k in df_chunk[col]]
                    elif dtype in ("jsonb"):
                        #df_chunk[col] = [json.dumps(k) if pd.notna(k) else k for k in df_chunk[col]]
                        df_chunk[col] = [json.dumps(k) for k in df_chunk[col]]
                #    elif dtype in ("real", "double precision", "numeric", "decimal"):
                #        df_chunk[col] = df_chunk[col].astype(float)
                #    elif dtype == "boolean":
                #        df_chunk[col] = df_chunk[col].astype(bool)
                #    # Text and other types remain as they are
                df_chunk.replace(to_replace=[np.nan,pd.NaT], value=None, inplace=True)
                chunks.append(df_chunk)

                if not rows:
                    break

            # Merge all chunks into a single DataFrame
            df = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
            ret_data['data'] = df
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def get_count(self, db, table, schema='public'):
        """
        This API is used to get the number of records in a table
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])

            # getting table vs master table from db
            sql = 'SELECT COUNT(*) from %s."%s"'
            self.mycursor.execute(query=sql %(schema,table))
            data = self.mycursor.fetchall()
            count, = data[0] if data else (0,)
            ret_data['data'] = count
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self._disconnect()
        return ret_data


    def update_table(self, db, table, ref_col, ref_col_index, update_col, update_value, schema='public'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.lock_table(db=db, table=table, schema=schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            sql = "UPDATE %s.%s set %s = %s WHERE %s = %s"
            self.mycursor.execute(query=sql %(schema, table, update_col, update_value, ref_col, ref_col_index))
            ret = self.commit()
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            #logging.debug('Update table : %s' %table)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def create_database(self, db):
        """
        This api will create a database
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            self._connect_raw()
            self.connection.autocommit = True
            self.mycursor = self.connection.cursor()
            self.mycursor.execute(query='create database %s' %(db,))
            #logging.debug('Created database : %s' %db)
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self._disconnect()
        return ret_data
        

    def delete_database(self, db):
        """
        This api will create a database
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db='postgres')
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            self.connection.autocommit = True
            self.mycursor = self.connection.cursor()
            terminate_process = "select pg_terminate_backend (pg_stat_activity.pid) from pg_stat_activity where pg_stat_activity.datname = '%s'"
            drop_db = 'DROP DATABASE IF EXISTS %s'
            #self.mycursor.execute('drop database %s' %db)
            self.mycursor.execute(query=terminate_process %(db,))
            self.mycursor.execute(query=drop_db %(db,))
            #logging.debug('Deleted database : %s' %db)
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self._disconnect()
        return ret_data

 
    def create_table(self, db, table, attrs, schema='public'):
        """
            This api will create a database table
            attrs can be of type: list or type: string
            if type = 'list' it should be ',' comma seperated fields as shown below:
                Ex: ['id,int(20),not null,primary key,auto_increment', 'name,varchar(20),not null']
            if type = 'string' it should be as shown below:
                Ex: 'id int(20) not null primary key auto_increment, name varchar(20) not null'
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            if isinstance(attrs, list):
                _attrs = ''
                for i in attrs:
                    i = re.sub(',',' ',i)
                    i = re.sub(r'\|',',',i)
                    _attrs += "%s, " %i
                attrs = _attrs.strip(', ')
            sql = "create table %s.%s (%s);"
            self.mycursor.execute(query=sql %(schema,table,attrs))
            #logging.debug('Created table : %s' %table)
            ret = self.commit()
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self._disconnect()
        return ret_data


    def create_schema(self, db, schema):
        """
            This api will create a schema if it doesn't exist in the given database
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            sql = "create schema if not exists %s;" %(schema)
            self.mycursor.execute(sql)
            ret = self.commit()
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self._disconnect()
        return ret_data


    def create_tables_from_df(self, db, df, _schema='Schema', _table='Table', _column='Column', _default='Default', _datatype='DataType', _add_created_at=False, _column_created_at='_created_at', _datatype_created_at='timestamp with time zone', _default_created_at='current_timestamp', overwrite=False):
        """
            This api will create database tables from dataframe
            dataframe must be in the following format:
                           Table                  Column DataType Default  Schema
            0     product_master         ingredient_code  varchar     NaN  public
            1     product_master         ingredient_name  varchar     NaN  public 
            2     product_master  ingredient_description  varchar     NaN  public
            3     product_master    like_ingredient_code  varchar     NaN  public
            4     product_master            channel_code  varchar     NaN  public

            if _add_created_at is True then it will check and add a row in each table if _column_created_at(_created_at) doesn't exist
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            # initialize
            _public = 'public'
            _cmds = []
            _sp_keys_def_pattern = r'current_date|current_timestamp|current_time|now\(\)|current_user|session_user|user|gen_random_uuid\(\)|uuid_generate_v4\(\)|pg_sleep\(*\)|true|false|interval|array'

            if _schema not in df: df[_schema] = _public
            
            schemas = df[_schema].unique()
            for schema in schemas:
                # create schema if it doesn't exist
                ret = self.create_schema(db=db, schema=schema)
                if ret['status'] == 'failed': raise exception(ret['err_msg'])

                _df = df[(df[_schema] == schema)]
                tables = _df[_table].unique()
                for table in tables:
                    _attrs = ''
                    _df = df[(df[_schema] == schema) & (df[_table]==table)]

                    if _add_created_at:
                        cols = len(list(_df.loc[(_df[_column] == _column_created_at), _column].values))
                        if cols == 0:
                            # Adding created_at column automatically if the dataframe doesn't have it
                            created_at_col = {_column:_column_created_at, _datatype:_datatype_created_at, _default:_default_created_at}
                            _df = _df._append(created_at_col, ignore_index=True)
                        
                    columns = _df[_column].unique()
                    for column in columns:
                        str_match = re.search(_sp_keys_def_pattern, _df.loc[_df[_column]==column, _default].values[0], re.I) if _df.loc[_df[_column]==column, _default].values[0] is not np.nan else False
                        if str_match:
                            _attrs += ("%s %s %s %s" %(column, _df.loc[_df[_column]==column, _datatype].values[0], _default, _df.loc[_df[_column]==column, _default].values[0]) if not pd.isna(_df.loc[_df[_column]==column, _default].values[0]) else "%s %s" %(column, _df.loc[_df[_column]==column, _datatype].values[0])) + ', '
                        else:
                            _attrs += ("%s %s %s '%s'" %(column, _df.loc[_df[_column]==column, _datatype].values[0], _default, _df.loc[_df[_column]==column, _default].values[0]) if not pd.isna(_df.loc[_df[_column]==column, _default].values[0]) else "%s %s" %(column, _df.loc[_df[_column]==column, _datatype].values[0])) + ', '
                    _cmd = 'create table %s.%s (%s)' %(schema, table, _attrs.strip(', '))
                    _cmds.append(_cmd)

            if overwrite:
                # delete db here
                ret = self.delete_database(db=db)
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])

                # create a new db here
                ret = self.create_database(db=db)
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])

            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
           
            for _cmd in _cmds:
                self.mycursor.execute(_cmd)
            
            ret = self.commit()
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])

        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self._disconnect()
        return ret_data


    def cleanup_stale_records(self, db, table, schema='public', column='created_at', duration='1 year'):
        """
            This api will aid in cleaning up old records for database table
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.lock_table(db=db, table=table)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            sql = "DELETE FROM %s.%s.%s WHERE %s < NOW() - INTERVAL '%s'"
            self.mycursor.execute(query=sql %(db, schema, table, column, duration))
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def delete_table(self, db, table, schema='public'):
        """
            This api will delete a database table
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.lock_table(db=db, table=table)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            sql = "drop table %s.%s.%s"
            self.mycursor.execute(query=sql %(db, schema, table))
            #logging.debug('Deleted table : %s' %table)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def _drop_keys(self, db, table, schema='public'):
        """
            This is an internal api used to drop an unique key or primary key from the column
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.lock_table(db=db, table=table, schema=schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            self.mycursor.execute(query='show indexes from %s.%s' %(schema,table))
            indexes = list(self.mycursor)
            keynames = []
            for index in indexes:
                if re.search('^PRIMARY$', index[2], re.M|re.I):
                    self.mycursor.execute(query='alter table %s.%s modify %s int, drop primary key' %(schema,table,index[4]))
                else:
                    keynames.append(index[2])
            keynames = list(set(keynames))
            for key in keynames:
                self.mycursor.execute(query='alter table %s.%s drop index %s' %(schema,table,key))
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def setup_database(self, tables='tables', schema='public', sql_data=None):
        """
        This API will setup the database as per the input provided by the inputmodule
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            if sql_data == None:
                ret = self.i.get_data(key='mysql')
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                self.mysqlData = ret['data']
                sql_data = self.mysqlData
            self.host = sql_data['host']
            self.user = sql_data['user']
            self.db = sql_data['database']
            logging.debug('Setting up Database : "%s"' %self.db)
            self.delete_stale_columns = sql_data['delete_stale_columns']
            ret = self.c.decrypt(sql_data['password'])
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            self.password = ret['data']
            ret = self._connect_raw(self.host, self.user, self.password)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            # check if db exists or else create one
            ret = self.isdatabase_exists(db=self.db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            if not ret['data']:
                ret = self.create_database(db=self.db)
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            tables = sql_data[tables]
            for table in tables:
                ret = self.istable_exists(db=self.db,table=table,schema=schema)
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                if not ret['data']:
                    # create a new table since table doesn't exist
                    attrs = tables[table]
                    ret = self.create_table(db=self.db,table=table,schema=schema,attrs=attrs)
                    if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                else:
                    ret = self._drop_keys(db=self.db,table=table,schema=schema)
                    if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                    # modify/add each column based on user input
                    ret = self._get_columns(db=self.db,table=table,schema=schema)
                    if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                    sqlcols = ret['data']
                    cfgcols = []
                    for cfgitem in tables[table]:
                        cfgitem = cfgitem.split(',')
                        cfgcol = cfgitem[0]
                        cfgcols.append(cfgcol)
                        if cfgcol in sqlcols:
                            if re.search(r'^oldname:\S+', cfgitem[-1], re.M|re.I):
                                cfgitem.pop()
                            colattrs = ' '.join(cfgitem)
                            ret = self.modify_column(db=self.db, table=table, schema=schema, colattrs=colattrs)
                            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                        elif re.search('UNIQUE', cfgcol):
                            colattrs = ' '.join(cfgitem)
                            colattrs = re.sub(r'\|',',',colattrs)
                            ret = self.add_unique_constraint(db=self.db, table=table, schema=schema, colattrs=colattrs)
                            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                        else:
                            if re.search(r'^oldname:\S+', cfgitem[-1], re.M|re.I):
                                oldcol = cfgitem.pop()
                                oldcol = re.sub('oldname:', '', oldcol)
                                colattrs = ' '.join(cfgitem)
                                ret = self.rename_column(db=self.db, table=table, schema=schema, oldcol=oldcol, colattrs=colattrs)
                                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                            else:
                                # check if the column matches if checked case-insensitive
                                colattrs = ' '.join(cfgitem)
                                colfound = False
                                for sqlcol in sqlcols:
                                    if re.search('^%s$' %cfgcol, sqlcol, re.M|re.I):
                                        colfound = True
                                        break
                                if colfound:
                                    ret = self.rename_column(db=self.db, table=table, schema=schema, oldcol=sqlcol, colattrs=colattrs)
                                    if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                                else:
                                    ret = self.add_column(db=self.db, table=table, schema=schema, colattrs=colattrs)
                                    if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                    if self.delete_stale_columns:
                        ret = self._get_columns(db=self.db, table=table, schema=schema)
                        if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                        sqlcols = ret['data']
                        isequal, _, _, diff_sql_cols = self.p.compare_list(cfgcols, sqlcols)
                        if not isequal:
                            ret = self.delete_columns(db=self.db, table=table, schema=schema, columns=diff_sql_cols)
                            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.i.clear_oldname_tag()    
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self._disconnect()
        return ret_data


    def add_column(self, db, table, colattrs, schema='public'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.lock_table(db=db, table=table, schema=schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            self.mycursor.execute(query='alter table %s.%s add %s' %(schema, table, colattrs))
            logging.debug('Added column: %s' %str(colattrs))
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data

     
    def rename_column(self, db, table, oldcol, colattrs, schema='public'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.lock_table(db=db, table=table, schema=schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            self.mycursor.execute(query='alter table %s.%s change %s %s' %(schema, table, oldcol, colattrs))
            logging.debug('Renamed column: %s' %str(colattrs))
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def modify_column(self, db, table, colattrs, schema='public'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.lock_table(db=db, table=table, schema=schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            self.mycursor.execute(query='alter table %s.%s modify %s' %(schema, table, colattrs))
            logging.debug('Update column: %s' %str(colattrs))
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def add_unique_constraint(self, db, table, colattrs, schema='public'):
        """
            This api helps in adding combined unique contraint
            E.g: if combination of lab_name & device need to be unique
            And not just lab_name unique or device unique
            User can add UNIQUE,(col1|col2|col3|...) in the config.json with a '|' delimeter
            This api will help in adding this contraint to mysql database
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.lock_table(db=db, table=table, schema=schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            self.mycursor.execute(query='alter table %s.%s add %s' %(schema, table, colattrs))
            logging.debug('Added Unique Constraint: %s' %str(colattrs))
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def delete_columns(self, db, table, columns, schema='public'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.lock_table(db=db, table=table, schema=schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            for col in columns:
                self.mycursor.execute(query='alter table %s.%s drop %s' %(schema, table, col))
            logging.debug('Deleted columns: %s' %str(columns))
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data

 
    def _get_columns(self, db, table, schema='public'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            ret = self.describe_table(db=db,table=table,schema=schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            columns = ret['data']
            colnames = []
            for col in columns:
                colnames.append(col)
            ret_data['data'] = colnames
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self._disconnect()
        return ret_data


    def lock_table(self, db, table, schema='public', mode='write'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            if self.connection_less:
                pass
                #ret = self._select_database(db)
                #if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                #self.mycursor.execute('lock tables %s %s' %(table, mode)) 
                #logging.debug('Table is locked (write): %s' %table)
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def unlock_table(self, db, table='', schema='public'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            if self.connection_less:
                self.connection.commit()
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def start_transaction(self):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            self.mycursor.execute('start transaction') 
            logging.debug('Start Transaction')
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def savepoint(self, savepoint):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            self.mycursor.execute(query='savepoint %s' %(savepoint,)) 
            logging.debug('Save point : %s' %savepoint)
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data

    
    def rollback(self, savepoint=None):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            if savepoint == None:
                self.mycursor.execute('rollback')
            else:
                self.mycursor.execute(query='rollback to %s' %(savepoint,))
            logging.debug('Rolled back to: %s' %savepoint)
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _ondup_format(self, collist):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ondup_fmt1 = ''
            ondup_fmt2 = ''
            for col in collist:
                ondup_fmt1 += '"%s", ' %col
                ondup_fmt2 += 'EXCLUDED."%s", ' %col
            ondup_fmt1 = ondup_fmt1.strip(', ')
            ondup_fmt2 = ondup_fmt2.strip(', ')
            if len(collist) > 1:
                ret_data['data'] = '(%s) = (%s)' %(ondup_fmt1, ondup_fmt2)
            else:
                # Adding fix for tables which has single column
                ret_data['data'] = '%s = %s' %(ondup_fmt1, ondup_fmt2)
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _format_values(self, vallist):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            vals = ''
            for val in vallist:
                r = ''
                for v in val:
                    if v == 'CURRENT_TIMESTAMP':
                        r += '%s, ' %v
                    elif isinstance(v, int):
                        r += '%s, ' %v
                    elif v == None:
                        r += 'null, '
                    else:
                        if isinstance(v, str): v = v.replace("'","''")
                        r += "'%s', " %v
                r = r.strip(', ')
                vals += '(%s), ' %r
            vals = vals.strip(', ')        
            ret_data['data'] = vals
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _get_col_val_list_from_dataframe(self, df, transpose=True):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            j = df.transpose() if transpose else df
            vallist = [list(j[k]) for k in j]
            collist = list(df)
            ret_data['data'] = (collist, vallist)
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _format_delete_query(self, df:pd.DataFrame):
        """
        This function helps in converting a dataframe to 
        "Where key1 in ('value1', 'value2'..) AND key2 in ('value1', 'value2'..)" sql query
        to be utilized by delete_rows function
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            df.dropna(axis=1, inplace=True)
            collist, vallist = self._get_col_val_list_from_dataframe(df=df, transpose=False)['data']
            sql_query = 'WHERE ' if collist else ''
            for col,val in zip(collist, vallist):
                _val = self._format_values(vallist=[val])['data']
                sql_query += '%s IN %s AND ' %(col, _val)
            sql_query = sql_query.strip(' AND ')
            ret_data['data'] = sql_query
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def _get_primary_key(self, db, table, schema='public'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            # nspname = 'public'
            # sql_query = f"""SELECT
            #                   pg_attribute.attname 
            #                 FROM pg_index, pg_class, pg_attribute, pg_namespace
            #                 WHERE 
            #                   pg_class.oid = '{table}'::regclass AND
            #                   indrelid = pg_class.oid AND 
            #                   nspname = '{nspname}' AND
            #                   pg_class.relnamespace = pg_namespace.oid AND
            #                   pg_attribute.attrelid = pg_class.oid AND 
            #                   pg_attribute.attnum = any(pg_index.indkey)
            #                  AND indisprimary"""

            # sql_query = f"""SELECT                                    
            #                 kcu.column_name
            #                 FROM 
            #                     information_schema.table_constraints tc
            #                 JOIN 
            #                     information_schema.key_column_usage kcu
            #                 ON 
            #                     tc.constraint_name = kcu.constraint_name
            #                     AND tc.table_schema = kcu.table_schema
            #                 WHERE 
            #                     tc.constraint_type = 'PRIMARY KEY'
            #                     AND tc.table_name = '{schema}.{table}';"""

            sql_query = """
                SELECT
                    kcu.column_name
                FROM
                    information_schema.table_constraints tc
                JOIN
                    information_schema.key_column_usage kcu
                ON
                    tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE
                    tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_name = '%s'
                    AND tc.table_schema = '%s';
            """

            self.mycursor.execute(query=sql_query %(table,schema))
            ret = self.mycursor.fetchall()
            pkey = [k for k, in ret]
            ret_data['data'] = pkey
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        return ret_data


    def get_primary_key(self, db, table, schema='public'):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            # connect to database
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])

            sql_query = """SELECT                                    
                            kcu.column_name
                            FROM 
                                information_schema.table_constraints tc
                            JOIN 
                                information_schema.key_column_usage kcu
                            ON 
                                tc.constraint_name = kcu.constraint_name
                                AND tc.table_schema = kcu.table_schema
                            WHERE 
                                tc.constraint_type = 'PRIMARY KEY'
                                AND tc.table_name = '%s'
                                AND tc.table_schema = '%s';"""
            self.mycursor.execute(query=sql_query %(table,schema))
            ret = self.mycursor.fetchall()
            pkey = [k for k, in ret]
            ret_data['data'] = pkey
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def add_rows(self, db, table, df, schema='public', onDupKeyOverwrite=False, disp=False):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            # connect to database
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])

            if not df.empty:
                # Define target table and columns
                # wrap each column with double quotes so that columns with reserved keywords like "table" will also be handled safely
                columns_format = ', '.join([f'"{col}"' for col in df.columns])
                
                
                # values format
                values_format = ', '.join(['%s' for i in df.columns])
                    
                if onDupKeyOverwrite:
                    # get primary key or composite primary key
                    ret = self._get_primary_key(db=db, table=table, schema=schema)
                    if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                    pkey = ret['data']

                    # keep only the latest row from duplicate rows from dataset
                    if pkey:
                        df.drop_duplicates(subset=pkey, keep='last', inplace=True)
                    else:
                        df.drop_duplicates(keep='last', inplace=True)
                    
                    # coverting pkey list to comma seperated string
                    # this is needed if pkey is a composite primary keys
                    pkey = ','.join(['"%s"' %i for i in pkey])

                    # Convert DataFrame to a list of tuples
                    data = df.itertuples(index=False, name=None)
                    
                    # get ondup values format
                    ret = self._ondup_format(collist=df.columns)
                    if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                    ondup_vals = ret['data']

                    # adding data to database
                    if pkey:
                        #self.mycursor.execute(f'insert into "%s" (%s) values %s on conflict ({pkey}) do update set %s' %(table, cols, values, ondup_vals))
                        # Adding fix for case insensitive names of tables
                        query = f'insert into {schema}."{table}" ({columns_format}) values ({values_format}) on conflict ({pkey}) do update set {ondup_vals}'
                        #try: execute_values(self.mycursor, query, data)
                        try: self.mycursor.executemany(query=query, params_seq=data)
                        except Exception as e:
                            print('ERROR: %s' %e)
                    else:
                        #self.mycursor.execute('insert into "%s" (%s) values %s' %(table, cols, values))
                        # Adding fix for case insensitive names of tables
                        query = f'insert into {schema}."{table}" ({columns_format}) values ({values_format})'
                        #execute_values(self.mycursor, query, data)
                        try: self.mycursor.executemany(query=query, params_seq=data)
                        except Exception as e:
                            print('ERROR: %s' %e)
                else:
                    # Convert DataFrame to a list of tuples
                    data = df.itertuples(index=False, name=None)
                    
                    # adding data to database
                    #self.mycursor.execute('insert into "%s" (%s) values %s' %(table, cols, values))
                    # Adding fix for case insensitive names of tables
                    query = f'insert into {schema}."{table}" ({columns_format}) values ({values_format})'
                    #execute_values(self.mycursor, query, data)
                    try: self.mycursor.executemany(query=query, params_seq=data)
                    except Exception as e:
                        print('ERROR: %s' %e)

                ret = self.commit()
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def add_rows2(self, db, table, df, schema='public', onDupKeyOverwrite=False, disp=False):
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            # connect to database
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])

            if onDupKeyOverwrite:
                # get primary key or composite primary key
                ret = self._get_primary_key(db=db, table=table, schema=schema)
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                pkey = ret['data']

                # keep only the latest row from duplicate rows from dataset
                if pkey:
                    df.drop_duplicates(subset=pkey, keep='last', inplace=True)
                else:
                    df.drop_duplicates(keep='last', inplace=True)
                
                # coverting pkey list to comma seperated string
                # this is needed if pkey is a composite primary keys
                pkey = ','.join(['"%s"' %i for i in pkey])

            # convert dataframe to collist and vallist
            collist, vallist = self._get_col_val_list_from_dataframe(df=df, transpose=True)['data']

            # convert cols to comma separated string
            cols = ','.join(['"%s"' %i for i in collist])

            # format values
            # ret = self._format_values(vallist=vallist)
            # if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            # values = ret['data']

            # if disp:
            #     logging.debug('Write table:\n\n%s\nValues: %s\n' %(table,values))
            # ret = self.lock_table(db=db, table=table)
            # if ret['status'] == 'failed': raise Exception(ret['err_msg'])

            if onDupKeyOverwrite:
                # get ondup values format
                ret = self._ondup_format(collist=collist)
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                ondup_vals = ret['data']

                # adding data to database
                if pkey:
                    #self.mycursor.execute(f'insert into "%s" (%s) values %s on conflict ({pkey}) do update set %s' %(table, cols, values, ondup_vals))
                    query = f'insert into {schema}.{table} ({cols}) values %s on conflict ({pkey}) do update set {ondup_vals}'
                    #execute_values(self.mycursor, query, vallist)
                    self.mycursor.executemany(query=query, params_seq=vallist)
                else:
                    #self.mycursor.execute('insert into "%s" (%s) values %s' %(table, cols, values))
                    query = f'insert into {schema}.{table} ({cols}) values %s'
                    #execute_values(self.mycursor, query, vallist)
                    self.mycursor.executemany(query=query, params_seq=vallist)
            else:
                # adding data to database
                #self.mycursor.execute('insert into "%s" (%s) values %s' %(table, cols, values))
                query = f'insert into {schema}.{table} ({cols}) values %s'
                #execute_values(self.mycursor, query, vallist)
                self.mycursor.executemany(query=query, params_seq=vallist)
            ret = self.commit()
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def delete_rows_raw(self, db, table, schema='public', query=None, disp=True):
        """
        This api is used to delete rows from a table
        if query = None then all rows will be deleted from the table
        query is a list input, if query list is provided then all rows
        with given unique ids will be deleted from the table
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            if query==None:
                sql = "delete from %s.%s" %(schema,table)
            else:
                sql = "delete from %s.%s where %s"
            ret = self.lock_table(db=db, table=table, schema=schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            self.mycursor.execute(query=sql %(schema, table, query))
            ret = self.commit()
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            if disp:
                logging.debug('Deleted rows from schema/table : %s/%s' %(schema,table))
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def delete_rows(self, db, table, df:pd.DataFrame, schema='public', disp=False):
        """
        This api is used to delete rows from a table
        if query = None then all rows will be deleted from the table
        query is a list input, if query list is provided then all rows
        with given unique ids will be deleted from the table
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])

            if not df.empty:
                ret = self._format_delete_query(df=df)
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                delete_query = ret['data']
                # logging.debug(delete_query)
                sql = "delete from %s.%s %s"
                ret = self.lock_table(db=db, table=table, schema=schema)
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                self.mycursor.execute(query=sql %(schema, table, delete_query))
                ret = self.commit()
                if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                if disp: logging.debug('Deleted rows from schema/table : %s/%s' %(schema,table))
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self.unlock_table(db=db, table=table, schema=schema)
            self._disconnect()
        return ret_data


    def get_levelled_master_table_list(self, db=None):
        """
        This API is used to find the master table list from db in conjuction from class find_levelled_master_table_list
        Note: the key value pair of table -- mastertable can be generated from the following sql query (out of scope of this class)
        SELECT tc.table_name AS source_table, ccu.table_name AS target_table FROM information_schema.table_constraints AS tc JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name JOIN information_schema.constraint_column_usage AS ccu ON tc.constraint_name = ccu.constraint_name WHERE tc.constraint_type = 'FOREIGN KEY'
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        try:
            ret = self._connect(db=db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])

            # getting table vs master table from db
            sql = "SELECT DISTINCT source_table, target_table FROM (SELECT tc.table_name AS source_table, ccu.table_name AS target_table FROM information_schema.table_constraints AS tc JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name JOIN information_schema.constraint_column_usage AS ccu ON tc.constraint_name = ccu.constraint_name WHERE tc.constraint_type = 'FOREIGN KEY') AS subquery"
            self.mycursor.execute(sql)
            data = self.mycursor.fetchall()

            # getting all tables from db
            get_tables_sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' AND table_name <> 'spatial_ref_sys'"
            self.mycursor.execute(get_tables_sql)
            all_tables = self.mycursor.fetchall()
            # convert all_tables to list
            all_tables = [k for k, in all_tables]
           
            # fetch levelled master table list
            ret = self.f.fetch_levelled_master_table_list(data=data)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            levelled_master_table_list = ret['data']

            lmtl = []
            [[lmtl.append(k) for k in i] for i in levelled_master_table_list]

            # including tables which doesnt have any foreign key relations
            tables_wout_fk = [t for t in all_tables if t not in lmtl]
            #logging.info(' ----  TABLES WITHOUT FOREIGN KEY RELATIONS  ----')
            #for i in tables_wout_fk: logging.info('\t%-28s' %i)
            if levelled_master_table_list and tables_wout_fk:
                levelled_master_table_list[0] += tables_wout_fk
            elif not levelled_master_table_list and tables_wout_fk:
                levelled_master_table_list = [tables_wout_fk]

            ret_data['data'] = levelled_master_table_list
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            logging.error(err_msg)
        finally:
            self._disconnect()
        return ret_data


    def transfer_records(self, source_db, target_db, tables, source_schema='public', target_schema='public', start_offset=0, end_offset=0, total_records=0, chunk_size=10000):
        """
        This api will help in transferring data from a source database to target database with 500 records as a chunk size
        source_db is a key-value pair for source database details like
            
            source_db       : dictionary; with connection details of source db
            source_db = {
                'db' = 'source_db_name',
                'port': 'source_db_port',
                'user': 'source_db_username',
                'password': 'source_db_password',
                'host': 'source_db_hostname',
            }

            target_db       : dictionary; with connection details of target db
            target_db = {
                'db': 'target_db_name',
                'port': 'target_db_port',
                'user': 'target_db_username',
                'password': 'target_db_password',
                'host': 'target_db_hostname',
            }

            tables          : a list of tables; mandatory
            source_schema   : source db schema; optional; default public
            target_schema   : target db schema; optional; default public
            start_offset    : start offset of data to be transferred; default = 0
            end_offset      : end offset of data to be transferred; default = total records on source db
            total_records   : total records to be transferred starting from start_offset; default = total records on source db
            chunk_size      : integer; default=10000; <chunksize of each data transfer>
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        t0 = time.time()
        try:
            # loop here for each table
            for i,table in enumerate(tables):
                self._transfer_records(source_db,target_db,table,i+1,len(tables),source_schema,target_schema,start_offset,end_offset,total_records,chunk_size)

        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            print(err_msg)
            logging.error(err_msg)
        return ret_data


    def _transfer_records(self, source_db, target_db, table, table_no, total_tables, source_schema='public', target_schema='public', start_offset=0, end_offset=0, total_records=0, chunk_size=10000):
        """
        This api will help in transferring data from a source database to target database with 500 records as a chunk size
        source_db is a key-value pair for source database details like
            
            source_db       : dictionary; with connection details of source db
            source_db = {
                'db' = 'source_db_name',
                'port': 'source_db_port',
                'user': 'source_db_username',
                'password': 'source_db_password',
                'host': 'source_db_hostname',
            }

            target_db       : dictionary; with connection details of target db
            target_db = {
                'db': 'target_db_name',
                'port': 'target_db_port',
                'user': 'target_db_username',
                'password': 'target_db_password',
                'host': 'target_db_hostname',
            }

            table           : name of table ; mandatory
            table_no        : serial no of table
            total_tables    : total no of tables 
            source_schema   : source db schema; optional; default public
            target_schema   : target db schema; optional; default public
            start_offset    : start offset of data to be transferred; default = 0
            end_offset      : end offset of data to be transferred; default = total records on source db
            total_records   : total records to be transferred starting from start_offset; default = total records on source db
            chunk_size      : integer; default=10000; <chunksize of each data transfer>
        """
        ret_data = {'status': 'success', 'err_msg': '', 'data': ''}
        t0 = time.time()
        try:
            sdb = source_db.get('db')
            tdb = target_db.get('db')

            # Connect target db
            ret = self._connect(**target_db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            targetcur = self.mycursor
            targetcon = self.connection

            # Connect source db
            ret = self._connect(**source_db)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            sourcecur = self.mycursor
            sourcecon = self.connection

            # Set it to connection always on
            self.connection_less=False

            # Fetch total no of records in source table
            ret = self.get_count(db=sdb, table=table, schema=source_schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            t_records = ret['data']

            # Figure out total_records from input or source db
            if end_offset:
                total_records = end_offset - start_offset
            elif not total_records or total_records > t_records:
                total_records = t_records

            print('\n--------------------------------------------------------------------')
            logging.info('\n' +
                         '\n%40s%-40s' %("Index : ", "%s/%s" %(table_no,total_tables)) +
                         '\n%40s%-40s' %("Table : ", table) +
                         '\n%40s%-40s' %("Records : ", total_records) +
                         '\n%40s%-40s' %("Source db : ",sdb) +
                         '\n%40s%-40s' %("Source schema : ",source_schema) +
                         '\n%40s%-40s' %("Target db : ",tdb) +
                         '\n%40s%-40s' %("Target schema : ",target_schema))

            # Get primary key
            ret = self.get_primary_key(db=sdb, table=table, schema=source_schema)
            if ret['status'] == 'failed': raise Exception(ret['err_msg'])
            primary_key = ret['data'][0]

            print()
            # Fetch and Push Data to/from dbs
            end_offset=start_offset
            #_tx = time.time()
            bar_format = "{l_bar}{bar}| [{n_fmt}/{total_fmt}] |time/eta,{elapsed}s/{remaining}s|"
            #with tqdm(total=total_records-start_offset, desc='Transferring: r/w,0.00s/0.00s', unit_scale=False, bar_format=bar_format) as progress:
            with tqdm(total=total_records, desc='Transferring', unit_scale=False, bar_format=bar_format) as progress:
                for i in range(start_offset, start_offset+total_records, chunk_size):
                    # Get Data from source db
                    #_t0 = time.time()
                    self.mycursor = sourcecur
                    end_offset = end_offset+chunk_size if end_offset+chunk_size <= start_offset+total_records else start_offset+total_records
                    ret = self.get_table(db=sdb, table=table, schema=source_schema, raw_query='ORDER BY %s LIMIT %s-%s OFFSET %s' %(primary_key,end_offset,i,i))
                    if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                    df = ret['data']
                    #rt = time.time()-_t0

                    #_t0 = time.time()
                    # Add Data to target db
                    self.mycursor = targetcur
                    ret = self.add_rows(db=tdb, table=table, schema=target_schema, df=df, onDupKeyOverwrite=True)
                    if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                    #wt = time.time()-_t0

                    # Commit now
                    targetcon.commit()
                    #_tc=time.time()
                    #_td=_tc-_tx
                    #eta=(_td*(total_records-end_offset))/chunk_size
                    #ret=self.format_seconds(eta)
                    #if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                    #eta=ret['data']
                    #_tx=_tc
                    #tt = time.time()-t0
                    #ret = self.format_seconds(tt)
                    #if ret['status'] == 'failed': raise Exception(ret['err_msg'])
                    #tt = ret['data']
                    #print('\r=> Added rows to "%s/%s" = %s/%s => %0.6s%% => ETA: %s => TimeTaken: %s => fetchtime: %0.6s => pushtime: %0.6s' %(tdb,table,(end_offset-start_offset),total_records,((end_offset-start_offset)/total_records)*100, eta, tt, ft, pt),end='',flush=True)
                    #progress.set_description('Transferring: r/w,%0.4ss/%0.4ss' %(rt, wt))
                    progress.update(len(df))
                    del df
                #progress.set_description('[TARGET] db="%s", table="%s"' %(tdb,table))

            #print('\n')
            #logging.info('Data transfer finished\n--------------------------------------------------------------------\n')
        except Exception as e:
            err_msg = self.i.err_format(sys.exc_info(), __class__.__name__)
            ret_data = {'status': 'failed', 'err_msg': err_msg, 'data': ''}
            print(err_msg)
            logging.error(err_msg)
        finally:
            self.connection_less=True
            targetcur.close()
            targetcon.close()
            sourcecur.close()
            sourcecon.close()
        return ret_data
# EOF
