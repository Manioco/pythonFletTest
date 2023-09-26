import sqlite3


def db_execute(query, params = []):
    with sqlite3.connect(f'database.db') as con:
        cur = con.cursor()
        cur.execute(query, params)
        con.commit()
        print(f"Executed query: {query}")
        return cur.fetchall()


def get_max_id_from_table(table_name):
    query = f"SELECT MAX(id) FROM {table_name}"
    result = db_execute(query)
    return result[0][0] if result[0][0] else 0


def drop_table(table_name):
    if table_name not in list_table():
        print(f"Table {table_name} does not exist")
    else:
        query = f"DROP TABLE {table_name}"
        db_execute(query)


def create_table(table_name, columns=[]):
    if table_name in list_table():
        print(f"Table {table_name} already exists")
    else:
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        for column in columns:
            query += f"{column} text, "
        query = query[:-2] + ")"
        db_execute(query)


def list_table():
    query = "SELECT name FROM sqlite_master WHERE type='table'"
    result = db_execute(query)
    return [x[0] for x in result]


def bigger_id():
    bigger_id = 0
    tables = list_table()
    for table in tables:
        table_id = get_max_id_from_table(table)
        if table_id > bigger_id:
            bigger_id = table_id
    return bigger_id

def list_items_from_table(table_name, filter = None):
    query = f"SELECT * FROM {table_name}"
    if filter:
        query += f" WHERE {filter}"
    result = db_execute(query)
    return result


def insert(table_name, task_name):
    status = 0
    if task_name:
        db_execute(query=f'INSERT INTO {table_name} VALUES(?, ?)', params=[name, status])
        task_name.value = ''
        results = db_execute('SELECT * FROM tasks')
        update_task_list()