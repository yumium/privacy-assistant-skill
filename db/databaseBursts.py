import psycopg2, psycopg2.extensions, select, threading, sys, configparser, os

IOTR_BASE = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
CONFIG_PATH = IOTR_BASE + "/config/config.cfg"

class dbManager():
    
    def __init__(self, dbname=None, username=None, password=None, client_name=None): # client_name is the schema for the client
        CONFIG = configparser.ConfigParser()
        CONFIG.read(CONFIG_PATH)

        if dbname is None:
            dbname = CONFIG['postgresql']['database']
        if username is None:
            username = CONFIG['postgresql']['username']
        if password is None:
            password = CONFIG['postgresql']['password']
        
        if client_name is None:
            self.client_name = CONFIG['postgresql']['client_schema']    
        else:
            self.client_name = client_name

        try:
            sys.stdout.write("Connecting to database...")
            self.connection = psycopg2.connect("dbname=%(dbname)s user=%(username)s password=%(password)s" % {'dbname':dbname,'username':username,'password':password })
            print("ok")
        except Exception as e:
            print("error")
            print(e.args)

    def listen(self, channel, cb=None):
        try:
            conn = self.connection
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            curs = conn.cursor()
            curs.execute("LISTEN %s ;" % channel)
            stop = [False]
            def stopme(): 
                stop[0] = True
            def subp(): 
                while not stop[0]: # kill me with a sharp stick. 
                    if select.select([conn],[],[],5) == ([],[],[]):
                        # print("Timeout")
                        pass
                    else:
                        conn.poll()
                        while not stop[0] and conn.notifies:
                            notify = conn.notifies.pop(0)
                            # print("Got NOTIFY:", notify.pid, notify.channel, notify.payload)
                            if cb is not None:
                                cb(notify.payload)
            thread = threading.Thread(target=subp)
            thread.start()                
            return stopme
        except:
            print("listen error")
            return lambda: None
        

    def execute(self, query, data, all=True):
        """ 
        Execute the query with data on the postgres db 
        If `all` is False then only gets one entry matching the query
        """
        cur = self.connection.cursor()
        cur.execute(query, data)
        #colnames = [desc[0] for desc in cur.description]
        try:
            if all:
                output = cur.fetchall()
            else:
                output = cur.fetchone()
        except:
            output = ""
        
        self.connection.commit()
        cur.close()

        return output

    def register_device(self, device_name, device_manufacturer):
        device_id = self.execute(
            f"SELECT id FROM devices WHERE name = '{device_name}' AND manufacturer = '{device_manufacturer}'",
            None,
            all=False
        )

        if device_id is None:
            print("Registration failed. Device not found in database.")
            return

        device_id = device_id[0] # The returned result from the query is a tuple of answers from each statement executed

        self.execute(
            f"INSERT INTO {self.client_name}.devices(id) VALUES ('{device_id}')",None
        )

        self.execute(
            f'''
                INSERT INTO {self.client_name}.device_data_collection_controls
                SELECT DISTINCT P.device_id, P.purpose, C.control
                FROM device_data_collection_purpose P NATURAL LEFT OUTER JOIN device_data_collection_controls C
                WHERE device_id = '{device_id}'
            ''',None
        ) # natural join selects rows where controls are present and (device_id,purpose) in ..._purpose. It also adds (device_id,purpose) pairs in ..._purpose but not found in ..._controls and set control to be null, which is exactly what we want. We need DISTINCT as the same (device_id,purpose) pair can exist across many data_sources.

        self.execute(
            f'''
                INSERT INTO {self.client_name}.device_data_collection_urgent_controls
                SELECT id
                FROM device_data_collection_urgent_controls
                WHERE device_id = '{device_id}'
            ''',None
        )
    
    def closeConnection(self):
        self.connection.close()