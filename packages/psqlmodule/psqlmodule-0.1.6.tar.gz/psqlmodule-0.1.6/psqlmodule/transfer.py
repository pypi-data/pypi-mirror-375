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
source_db = {
    'db': 'dt_db3',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'host': 'dt_db'
}
source_schema = 'schema_'
target_db = {
    'db': 'dt_db4',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'host': 'dt_db'
}
target_schema = 'schema_'

import re
t = p.get_levelled_master_table_list(p.db)['data']
j = []
[j:=j+k for k in t]
tables = [k for k in j if not re.search('^django|^user|^auth|risk_activity|^tenants', k)]

p.transfer_records(source_db=source_db,target_db=target_db,tables=tables,source_schema=source_schema,target_schema=target_schema)
