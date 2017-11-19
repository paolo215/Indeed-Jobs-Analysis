import sqlite3
import os

class DB_Manager(object):
    def __init__(self):
        self.jobs_db = "jobs.sqlite"        
        self.conn = None
        self.cursor = None

        if os.path.exists(self.jobs_db):
            self.conn = sqlite3.connect(self.jobs_db)
            self.cursor = self.conn.cursor()
            print("Connected to db")
        else:
            self.create_new_db()

    def create_new_db(self):
        self.conn = sqlite3.connect(self.jobs_db)
        self.cursor = self.conn.cursor()
        self.create_indeed_jobs_table()
        self.create_indeed_jobs_tech_table()
        self.create_tech_table()
        self.create_keywords_table()


    def create_indeed_jobs_table(self):
        self.cursor.execute(        
        """
        CREATE TABLE IF NOT EXISTS indeed_jobs 
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
        self.conn.commit()

    def insert_job(self, job_id, job_title, job_url, search_job, search_location, location):
        try:
            self.cursor.execute(
            """
            INSERT INTO indeed_jobs
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
        CREATE TABLE IF NOT EXISTS keywords
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL UNIQUE,
            frequency INTEGER DEFAULT 0,
            recognized INTEGER DEFAULT 0,
            ignored INTEGER DEFAULT 0
        )
        """
        )

    def insert_keyword(self, name):
        try:
            self.cursor.execute(
            """
            INSERT INTO keywords
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
        CREATE TABLE IF NOT EXISTS indeed_jobs_tech
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            job_id INTEGER NOT NULL,
            tech_id INTEGER NOT NULL,
            FOREIGN KEY(job_id) REFERENCES indeed_jobs(job_id),
            FOREIGN KEY(tech_id) REFERENCES tech(id)
        )
        """)
        self.conn.commit()



    def insert_jobs_tech(self, job_id, tech_id):
        try:
            self.cursor.execute(
            """
            INSERT INTO indeed_jobs_tech
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
        CREATE TABLE IF NOT EXISTS tech
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL UNIQUE
        )
        """)


    def insert_tech(self, name):
        try:
            self.cursor.execute(
            """
            INSERT INTO tech
                (name)
                VALUES
                ('%s')
            """ % (name)
            )
            return True
        except sqlite3.IntegrityError:
            return False


    def close(self):
        self.conn.close()

