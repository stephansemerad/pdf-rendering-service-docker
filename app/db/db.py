import sqlite3, os
db_path = os.path.join( os.path.dirname(os.path.realpath(__file__)), 'pdf-rendering-service.db' )

def br(value):
    if value == 'None' or value == None: return 'NULL'
    try:value = value.decode('utf8')
    except:value = str(value)
    value.replace('<','').replace('>','')
    if value == '' or value ==None:value = 'NULL'
    else:value ="'"+ value.replace("'","") +"'"
    return value

def select(sql):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    data = cursor.execute(sql).fetchall()
    cursor.close()
    conn.close()
    return data

def insert(sql):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    lastrowid = cursor.lastrowid
    cursor.close()
    conn.close()
    return lastrowid

def update(sql):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    return True

def delete(sql):
    update(sql)

def set_up_db():
    sql_tables = open (os.path.join( os.path.dirname(os.path.realpath(__file__)), 'tables.sql' ), "r").read()
    sql_tables = sql_tables.split(';')
    for sql in sql_tables: insert(sql)


set_up_db()


# sql = '''
#         select pdf_id, filename, status, created_at, job_id, enqueued_at, processed_at,
#         (select count(1) from imgs where imgs.pdf_id = pdf_id)
#         from pdfs
#         order by created_at
#         limit 5
# '''
# data = select(sql)
# print(data)







