from shiny import render, ui
from shiny.express import input
import sqlite3
import pandas as pd
import ast
from datetime import datetime
import io
import random
import string

return_table = None

def process_table2(process_db):

    conv_table = process_db
    conv_tables = []
    for i in range(conv_table.shape[0]):
        data = pd.DataFrame(ast.literal_eval(conv_table["targets_ak"][i])[0], index = [0])

        ele = pd.DataFrame(ast.literal_eval(conv_table["targets_bk"][i]))

        ele["calc_vlc"] = data["vlc"][0]
        ele["measurement_ID"] = ''.join(random.choices(string.ascii_letters,
                             k=7))

        conv_tables.append(ele)

    conv_tables = pd.concat(conv_tables)

    return conv_tables

def process_table(process_db):
    timestamp = process_db

    timestamp = pd.to_datetime(timestamp["timestamp"], unit = "ms")

    conv_table = process_db
    conv_tables = []
    for i in range(conv_table.shape[0]):
        data = pd.DataFrame(ast.literal_eval(conv_table["targets_ak"][i])[0], index = [0])
        conv_tables.append(data)

    conv_tables = pd.concat(conv_tables)

    conv_tables["timestamp"] = timestamp

    return conv_tables

ui.panel_title("SQLite file reader [ak]")
ui.input_file("file1", "Choose a .db File", accept=[".db"], multiple=False)


@render.text
def txt():
    global return_table
    if input.file1() is not None:
        db = sqlite3.connect(input.file1()[0]['datapath'])
        tables = db.execute('''SELECT name FROM sqlite_master  
  WHERE type='table';''')
        tables = tables.fetchall()
        tables = [table[0] for table in tables if "test" in table[0]]

        pd_tables = [pd.read_sql_query(f"SELECT * from {table}", db) for table in tables]

        db.close()

        return_table = pd.concat([process_table(table) for table in pd_tables])
        return "File Ready, Please click Download"

@render.download(filename=f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}.csv")
def download():
    global return_table
    yield return_table.to_csv()
