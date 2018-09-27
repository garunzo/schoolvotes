import psycopg2

def print_rows(rows):
    for row in rows:
        print(row)
    return

try:
    connect_str = "dbname='schoolvotesdb' user='schoolvotesadmin' host='schoolvotes.crfmfmw2lj5n.us-east-2.rds.amazonaws.com' " + \
                  "password='kev-wx8-8JN-FpF'"
    # use our connection values to establish a connection
    conn = psycopg2.connect(connect_str)
    # create a psycopg2 cursor that can execute queries
    cursor = conn.cursor()
    # create a new table with a single column called "name"
    cursor.execute("""CREATE TABLE tutorials (name char(40));""")
    # run a SELECT statement - no data in there, but we can try it
    cursor.execute("""SELECT * from tutorials""")
    rows = cursor.fetchall()
    print(rows)
    cursor.execute("""SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'""")
    print_rows(cursor.fetchall())

except Exception as e:
    print("Uh oh, can't connect. Invalid dbname, user or password?")
    print(e)
