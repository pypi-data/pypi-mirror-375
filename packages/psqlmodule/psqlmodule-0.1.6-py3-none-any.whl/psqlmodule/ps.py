from psqlmodule.psqlmodule import *
import pandas as pd
from tqdm import tqdm
from uuid import uuid4, UUID
import importlib, traceback

p = psqlmodule()
schema = 'public'

def get_table_decorator(func):
    def wrapper(*args, **kwargs):
        kwargs['db'] = p.db
        kwargs['schema'] = schema
        kwargs['table'] = args[0]
        result = func(**kwargs)
        result['data'].attrs['name'] = args[0]
        return result['data']
    return wrapper

def add_rows_decorator(func):
    def wrapper(*args, **kwargs):
        kwargs['db'] = p.db
        kwargs['schema'] = schema
        kwargs['table'] = args[0]
        kwargs['df'] = args[1]
        kwargs['onDupKeyOverwrite'] = True
        result = func(**kwargs)
        return result
    return wrapper

def delete_rows_decorator(func):
    def wrapper(*args, **kwargs):
        kwargs['db'] = p.db
        kwargs['schema'] = schema
        kwargs['table'] = args[0]
        col1 = args[1].columns.to_list()[0]
        kwargs['df'] = args[1][[col1]]
        result = func(**kwargs)
        return result
    return wrapper

def load(arg):
    global schema, get, add, delete
    schema = arg
    get = get_table_decorator(p.get_table)
    add = add_rows_decorator(p.add_rows)
    delete = delete_rows_decorator(p.delete_rows)

def upload(file):
    try:
        tables = pd.read_excel(file, sheet_name='tables', engine='openpyxl')
        tabs = tables.loc[tables['upload'].eq(True)].sort_values(by='order')[['tabname','tables','delete','force']].to_dict(orient='records')

        with tqdm(total=len(tabs)) as pbar:
            for tab in tabs:
                pbar.set_description(f"Uploading [[{tab['tables']:^20.20}]]")

                tabledf = pd.read_excel(file, sheet_name=tab['tabname'], engine='openpyxl')

                # check if its delete or add operation
                if not tab['delete']:
                    tabledf = tabledf.replace({pd.NaT: None, np.nan: None})
                    add(tab['tables'], tabledf)
                elif not tab['force']:
                    check = input(f"Deleting records from {tab['tables']}, this is destructive process, do you want to continue (Y/n) : ")
                    if check.lower() == 'y':
                        delete(tab['tables'], tabledf.iloc[:,[0]])
                else:
                    delete(tab['tables'], tabledf.iloc[:,[0]])
 
                # move progress bar
                pbar.update(1)
                
    except Exception as e:
        print(f'ERROR: {e}')
        traceback.print_exc()

def getuuid(count=1):
    for i in range(count):
        print(uuid4())

def download_df(dfs, filename, tabs=[]):
    fname, ext = os.path.splitext(filename)
    if (ext != '.xlsx') and (ext != '.csv'):
        print('ERROR: Output file extension should be either .csv or .xlsx only')
        return
    if (not isinstance(dfs, list)) and (not isinstance(dfs, pd.DataFrame)):
        print('ERROR: Supported input datatypes "pd.DataFrame" or "list of pd.DataFrame" only')
        return
    if not isinstance(dfs, list):
        dfs = [dfs]

    fh = None
    if ext == '.xlsx':
        fh = pd.ExcelWriter(filename, engine='openpyxl')
    else:
        # if extension is .csv then no point in iterating multiple dfs, just store first df in the give file name
        dfs = dfs[:1]

    i=0;tabs = [k.attrs.get('name') if k.attrs.get('name') is not None else (i:=i+1, f'tab_{i}')[1] for k in dfs] if not tabs else tabs
    with tqdm(total=len(dfs)) as pbar:
        for (i,df),tab in zip(enumerate(dfs),tabs):
            df = convert_timezone_to_string(df)
            pbar.set_description(f"Downloading {filename} [[{tab:^20.20}]]")
            if fh:
                df.to_excel(fh, sheet_name=tab, index=False)
            else:
                df.to_csv(f'{fname}{ext}', index=False)
            pbar.update(1)
    if fh: fh.close()


def download(tables, filename):
    fname, ext = os.path.splitext(filename)
    if (ext != '.xlsx') and (ext != '.csv'):
        print('ERROR: Output file extension should be either .csv or .xlsx only')
        return
    if not isinstance(tables, list):
        tables = [tables]
    dfs = []
    for table in tables:
        dfs.append(get(table)) 
    download_df(dfs, filename)


def convert_timezone_to_string(df):
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].astype(str)
    return df

load(schema)
