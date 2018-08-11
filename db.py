import psycopg2

def print_rows(rows):
    for row in rows:
        print(row)

def select(text):
    base = 'select * from '
    end = ';'
    try:
        cur.execute(base + text + end)
    except Exception as error:
        print(error)
        return
    rows = cur.fetchall()
    return rows

def insert(to, *, values):
    base = 'insert into '
    middle = ' values '
    end = ';'
    cur.execute(base + to + middle + values + end)
    conn.commit()
    print('inserted the values\n{}'.format(values))

def execc(text):
    try:
        cur.execute(text)
    except Exception as err:
        print('We faced an error:\n{}'.format(err))

if __name__ == '__main__':
    host = input('host: ')
    user = input('user: ')
    password = input('password: ')
    dbname = input('dbname: ')
    try:
        conn = psycopg2.connect("dbname='{}' user='{}' host='{}' password='{}'".format(dbname, user, host, password))
    except Exception as error:
        print(error)
    cur = conn.cursor()
    while True:
        print('Modes: 1 = select, 2 = insert, 3 = execute, 4 = close.')
        choice = input('Mode: ')
        if choice not in '4':
            if choice == '1':
                text = input('Tell me where to select from: ')
                rows = select(text)
                print('Press enter to continue or type 1 to stop.')
                for row in rows:
                    print(row)
                    inp = input()
                    if inp == '1':
                        break
            elif choice == '2':
                to = input('Tell me where to insert to: ')
                values = input('Tell what to insert: ')
                insert(to, values=values)
            elif choice == '3':
                text = input('Type what to execute: ')
                execc(text)
        else:
            break
