import sqlite3
import os

class DB_Manager(object):
    def __init__(self):


        # Name of the db file
        self.jobs_db = "jobs.sqlite"        

        # SQLite DB connection
        self.conn = None

        # Row traversal 
        self.cursor = None

        # Store column names of the tables
        self.jobs_column_names = None
        self.jobs_tech_column_names = None
        self.keywords_column_names = None
        self.tech_column_names = None


        # Table names
        self.jobs_table_name = "indeed_jobs"
        self.jobs_tech_table_name = "indeed_jobs_tech"
        self.keywords_table_name = "keywords"
        self.tech_table_name = "tech"
        
        # Initializes db
        self.init_db()

    def init_db(self):
        """
        Connects to the database and attempts to set up the tables
        """
        
        # Connect to the database
        self.conn = sqlite3.connect(self.jobs_db)


        # Change default row_factory to dict_factory.
        # NOTE: Default return value of the queries are tuples. 
        # To me, that is not a good data structure
        # as we have to remember the index of every columns.
        # Converting this to dict_factory will make it more flexible
        self.conn.row_factory = self.dict_factory

        # Used for row traversal
        self.cursor = self.conn.cursor()

        # Set up tables
        self.create_indeed_jobs_table()
        self.create_indeed_jobs_tech_table()
        self.create_tech_table()
        self.create_keywords_table()


    def create_indeed_jobs_table(self):
        """
        Sets up indeed_jobs table
        """

        # Set up table
        self.cursor.execute(        
        """
        CREATE TABLE IF NOT EXISTS 
        """ + self.jobs_table_name + \
        """
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            job_id TEXT NOT NULL,
            title TEXT, 
            url TEXT,
            search_job TEXT,
            search_location TEXT,
            location TEXT,
            applied INT DEFAULT 0,
            viewed INT DEFAULT 0
        )
        """)

        # Obtain columns
        self.cursor.execute(
            "SELECT * FROM " + self.jobs_table_name
        )
        self.jobs_column_names = [f[0] for f in self.cursor.description]


        self.conn.commit()

    def insert_job(self, job_id, job_title, job_url, search_job, search_location, location):
        """
        Insert row into indeed_jobs table
        """

        try:
    
            # Insert row
            self.cursor.execute(
            """
            INSERT INTO
            """ + self.jobs_table_name + \
            """
                (job_id, title, url, search_job, search_location, location)
                VALUES
                ('%s','%s','%s','%s', '%s', '%s')
            """ % (job_id, job_title, job_url, search_job, search_location, location)
            )    
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return -1


    def create_keywords_table(self):
        """
        Sets up keywords table
        """

        # Set up keywords table
        self.cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS
        """ + self.keywords_table_name + \
        """
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL UNIQUE,
            frequency INTEGER DEFAULT 1,
            recognized INTEGER DEFAULT 0,
            ignored INTEGER DEFAULT 0
        )
        """
        )

        # Obtain columns
        self.cursor.execute(
            "SELECT * FROM " + self.keywords_table_name
        )
        self.keywords_column_names = [f[0] for f in self.cursor.description]
        self.conn.commit()


    def insert_keyword(self, name):
        """
        Insert row into keywords table

        """

        try:
            # Insert row
            self.cursor.execute(
            """
            INSERT INTO 
            """ + self.keywords_table_name + \
            """
                (name)
                VALUES
                ('%s')
            """ % (name)
            )

            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return -1

    def does_keyword_exists(self, name):
        try:
            print(name) 
            self.cursor.execute(
            "SELECT * from " + self.keywords_table_name + " where name = '%s'" % (name)
            )
            rows = self.cursor.fetchall()
            return True if rows else False
        except sqlite3.IntegrityError:
            return False

    def insert_or_update_keyword(self, name):
        if self.does_keyword_exists(name):
            is_recognized = self.does_exists_in_tech_table(name)
            is_recognized = 1 if is_recognized == True else 0
            return self.update_keyword_booleans_and_increment(name, is_recognized)
        else:
            print("new keyword: " + name)
            return self.insert_keyword(name)


    def update_keyword_booleans(self, name, is_recognized, is_ignored = 0):
       try:
            self.cursor.execute("UPDATE " + self.keywords_table_name + \
                " SET recognized = %d, ignored = %d where name = '%s'" % (is_recognized, is_ignored, str(name)))
            return self.cursor.lastrowid
       except sqlite3.IntegrityError:
            return -1


    def update_keyword_booleans_and_increment(self, name, is_recognized, is_ignored = 0):
       try:
            self.cursor.execute("UPDATE " + self.keywords_table_name + \
                " SET recognized = %d, ignored = %d, frequency = frequency + 1 where name = '%s'" % (is_recognized, is_ignored, str(name)))
            return self.cursor.lastrowid
       except sqlite3.IntegrityError:
            return False 

    def create_indeed_jobs_tech_table(self):
        """
        Set up indeed_jobs_tech table
        """

        # Set up table
        self.cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS 
        """ + self.jobs_tech_table_name + \
        """
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            job_id TEXT NOT NULL,
            tech_id INTEGER NOT NULL,
            FOREIGN KEY(job_id) REFERENCES indeed_jobs(job_id),
            FOREIGN KEY(tech_id) REFERENCES tech(id)
        )
        """)

        # Obtain columns
        self.cursor.execute(
            "SELECT * FROM " + self.jobs_tech_table_name
        )
        self.jobs_tech_column_names = [f[0] for f in self.cursor.description]
        self.conn.commit()



    def insert_jobs_tech(self, job_id, tech_id):
        """
        Insert row into jobs_tech table 
        """

        try:
            # Insert row to jobs_tech table
            self.cursor.execute(
            """
            INSERT INTO
            """ + self.jobs_tech_table_name + \
            """
                (job_id, tech_id)
                VALUES
                ('%s', '%s')
            """ % (job_id, tech_id)
            )
            return True
        except sqlite3.IntegrityError:
            return False


    def create_tech_table(self):
        """
        Sets up tech table
        """

        # Set up table
        self.cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS 
        """ + self.tech_table_name + \
        """
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL UNIQUE
        )
        """)

        # Obtain columns
        self.cursor.execute(
            "SELECT * FROM " + self.tech_table_name
        )
        self.tech_column_names = [f[0] for f in self.cursor.description]
        self.conn.commit()

    def insert_tech(self, name):
        """
        Insert row into tech table
        """

        try:
            # Insert row
            self.cursor.execute(
            """
            INSERT INTO
            """ + self.tech_table_name + \
            """
                (name)
                VALUES
                ('%s')
            """ % (name)
            )

            return True
        except sqlite3.IntegrityError:
            return False


    def does_exists_in_tech_table(self, name):
        try:
            self.cursor.execute(
            "SELECT * from " + self.tech_table_name + " where name = '%s' " % (name)
            )

            rows = self.cursor.fetchall()
            return True if rows else False
        except sqlite3.IntegrityError:
            return False

    def get_all_tech(self):
        """
        Retrieves all rows in tech table
        """
        try:
            # Select all rows
            self.cursor.execute("SELECT * FROM tech")

            # Fetch all rows
            rows = self.cursor.fetchall()
            return rows

        except sqlite3.IntegrityError:
            return None
    
    def get_all_tech_names(self):
        """
        Retrieves all names in tech table
        """
        try:

            # Select name of every rows in the table
            self.cursor.execute("SELECT name from tech")
            
            # Converts list of dictionary into list of names
            rows = [f["name"] for f in self.cursor.fetchall()]
            return rows
            
        except sqlite3.IntegrityError:
            return None
   
    def dict_factory(self, cursor, rows):
        """
        Converts each list of tuples into list of dictionaries
        """
        data = {}
        for idx, col in enumerate(cursor.description):
            data[col[0]] = rows[idx]

        return data


    def close(self):
        """
        Close connection to the database
        """
        self.conn.close()



    
