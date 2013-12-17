from __future__ import print_function

import pprint
import cmd
import pymssql
import string
    
PROMPT = "\033[94m{0}\033[0m ({1}) > "

class MsSqlShell(cmd.Cmd):
        intro = 'Welcome to the Microsoft SQL monitor.  Commands end with ; or \g. Type help or ? to list commands.\n'
        identchars = string.ascii_letters + string.digits + '_' + '-'
        
        def __init__(self, host=None, user=None, password=None, database=None):
            cmd.Cmd.__init__(self, completekey='TAB')
            
            self.host = host
            self.user = user
            self.password = password
            
            self.conn = pymssql.connect(host=host, user=user, password=password, database=database, charset="UTF-8")
            
            self.databases = self.get_databases()
            self.update_prompt()
            
            
        def get_current_database(self):
            cur = self.conn.cursor()
            try:
                cur.execute("SELECT DB_NAME()")
                row = cur.fetchone()
                return (row[0])
            finally:
                cur.close()
        
        def get_tables(self):
            try:
                cur = self.conn.cursor()
                cur.execute("SELECT name FROM sys.tables")
                tables = [(row[0]) for row in cur.fetchall()]
                return (tables)
            finally:
                cur.close()
            
        def get_databases(self):
            try:
                cur = self.conn.cursor()
                cur.execute("SELECT name FROM sys.databases")
                databases = [(row[0]) for row in cur.fetchall()]
                return (databases)
            finally:
                cur.close()
        
        def update_prompt(self):
            self.database = self.get_current_database()
            self.tables = self.get_tables()
            self.prompt = PROMPT.format(self.host, self.database)
            
        def do_use (self, rest):
            try:
                cur = self.conn.cursor()
                cur.execute('USE [{0}]'.format(rest))
                self.update_prompt()
            finally:
                cur.close()            
        
        def complete_use(self, text, line, begidx, endidx):
            options = [i for i in self.databases if i.startswith(text)]
            return (options)
    
        def default(self, line):
            try:
                cur = self.conn.cursor()
                cur.execute(line)
                
                if not cur.description:
                    return
                
                #3 -> int?
                #1 -> varchar
                #4 -> date?
                print ('|'.join(['{0:12}'.format(column[0]) for column in cur.description]))
                       
                row = cur.fetchone()
                while row:
                    print ('|'.join(['{0:12}'.format((str(column) if column else '')) for column in row]))
                    row = cur.fetchone()
    
                cur.close()
                
                if cur.rowcount>=0:
                    print ("Rows affected: {0}".format(cur.rowcount))
            except Exception, exc:
                print (exc)
                
            pass
        
        def completedefault(self, text, line, begidx, endidx):
            options = [i for i in self.tables if i.startswith(text)]
            return (options)

	def do_stop(self, rest):
	    return 1
	
	def help_stop(self):
	    print ("stop: terminates the command loop")

        def do_EOF(self, line):
            conn.close()
            return True

        
if __name__=='__main__':
        import argparse
        parser = argparse.ArgumentParser(description='Microsoft SQL Server client.')
        parser.add_argument('--host', '-H', help='Host')
        parser.add_argument('--user', '-u', help='User')
        parser.add_argument('--password', '-p', help='Password')
        parser.add_argument('--database', '-d', help='Database')
        args = parser.parse_args()
        print ("Connecting to {0}".format(args.host))
        
        s = MsSqlShell(**vars(args))
	while True:
		try:
			s.cmdloop()
		except Exception, exc:
			print (exc)
