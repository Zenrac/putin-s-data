import psycopg2

class Config():
    def __init__(self, tablename):
        self.tablename = tablename
        self.conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='postgres'")
        self.cur = self.conn.cursor()

    def get(self, asqd, value, what = '*'):
        self.cur.execute('select {} from {} where {} = {}'.format(what, self.tablename, asqd, value))
        rowsss = str(self.cur.fetchall())
        rowss = rowsss.replace('(', '')
        rows = rowss.replace(',)', '')
        return rows

    def put(self, wwhat, iss, asqd, value):
        try:
            self.cur.execute('update {} set {} = {} where {} = {}'.format(self.tablename, asqd, value, wwhat, iss))
            print('update {} set {} = {} where {} = {}'.format(self.tablename, asqd, value, wwhat, iss))
            self.conn.commit()
            return True
        except Exception as e:
            return 'False\n{}'.format(e)

    def make(self, asqd):
        try:
            self.cur.execute('insert into {} values ({})'.format(self.tablename, asqd))
            print('insert into {} values ({})'.format(self.tablename, asqd))
            self.conn.commit()
            return True
        except Exception as e:
            return 'False\n{}'.format(e)
#
# import dbconfig
# config = dbconfig.Config('profiles')
