import sqlite3
import os

class DB_Manager(object):
    def __init__(self):
        self.jobs_db = "jobs.sqlite"        
        self.conn = None
        self.cursor = None

        self.jobs_column_names = None
        self.jobs_tech_column_names = None
        self.keywords_column_names = None
        self.tech_column_names = None


        self.jobs_table_name = "indeed_jobs"
        self.jobs_tech_table_name = "indeed_jobs_tech"
        self.keywords_table_name = "keywords"
        self.tech_table_name = "tech"
        

        self.create_new_db()

    def create_new_db(self):
        self.conn = sqlite3.connect(self.jobs_db)
        self.conn.row_factory = self.dict_factory
        self.cursor = self.conn.cursor()
        self.create_indeed_jobs_table()
        self.create_indeed_jobs_tech_table()
        self.create_tech_table()
        self.create_keywords_table()


    def create_indeed_jobs_table(self):
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

        self.cursor.execute(
            "SELECT * FROM " + self.jobs_table_name
        )
        self.jobs_column_names = [f[0] for f in self.cursor.description]
        self.conn.commit()

    def insert_job(self, job_id, job_title, job_url, search_job, search_location, location):
        try:
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
            return True
        except sqlite3.IntegrityError:
            return False


    def create_keywords_table(self):
        self.cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS
        """ + self.keywords_table_name + \
        """
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL UNIQUE,
            frequency INTEGER DEFAULT 0,
            recognized INTEGER DEFAULT 0,
            ignored INTEGER DEFAULT 0
        )
        """
        )
        self.cursor.execute(
            "SELECT * FROM " + self.keywords_table_name
        )
        self.keywords_column_names = [f[0] for f in self.cursor.description]
        self.conn.commit()

    def insert_keyword(self, name):
        try:
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
            return True
        except sqlite3.IntegrityError:
            return False

    def create_indeed_jobs_tech_table(self):
        self.cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS 
        """ + self.jobs_tech_table_name + \
        """
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            job_id INTEGER NOT NULL,
            tech_id INTEGER NOT NULL,
            FOREIGN KEY(job_id) REFERENCES indeed_jobs(job_id),
            FOREIGN KEY(tech_id) REFERENCES tech(id)
        )
        """)
        self.cursor.execute(
            "SELECT * FROM " + self.jobs_tech_table_name
        )
        self.jobs_tech_column_names = [f[0] for f in self.cursor.description]
        self.conn.commit()



    def insert_jobs_tech(self, job_id, tech_id):
        try:
            self.cursor.execute(
            """
            INSERT INTO
            """ + self.tech_table_name + \
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
        self.cursor.execute(
            "SELECT * FROM " + self.tech_table_name
        )
        self.tech_column_names = [f[0] for f in self.cursor.description]
        self.conn.commit()

    def insert_tech(self, name):
        try:
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

    def get_all_tech(self):
        try:
            self.cursor.execute("SELECT * FROM tech")

            rows = self.cursor.fetchall()
            return rows

        except sqlite3.IntegrityError:
            return None
    
   
    def dict_factory(self, cursor, rows):
        data = {}
        for idx, col in enumerate(cursor.description):
            data[col[0]] = rows[idx]

        return data


    def close(self):
        self.conn.close()



    
