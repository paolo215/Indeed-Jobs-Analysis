import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import os
import re
import sqlite3
import time

keywords = "keywords.txt"


class SQLiteDB(object):
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
        self.cursor.execute(        
        """
        CREATE TABLE jobs 
        (
            id TEXT PRIMARY KEY, 
            title TEXT, 
            url TEXT,
            search_job TEXT,
            search_location TEXT,
            location TEXT,
            count INT 
        )
        """)
        self.conn.commit()
        print("Created db")


    def insert(self, job_id, job_title, job_url, search_job, search_location, location, count):
        try:
            self.cursor.execute(
            """
            INSERT INTO jobs
                (id, title, url, search_job, search_location, location, count)
                VALUES
                ('%s','%s','%s','%s', '%s', '%s', %s)
            """ % (job_id, job_title, job_url, search_job, search_location, location, count)
            )    
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def close(self):
        self.conn.close()


class IndeedCrawler(object):
    def __init__(self, keywords_filename):
        self.keywords_filename = keywords_filename
        self.base_url = "https://www.indeed.com/"
        self.keywords = self.__get_keywords()
        self.db = SQLiteDB()

    def get_content(self, url):
        return requests.get(url, headers={"Accept-Encoding" : "identity"}).content


    def search(self, job, location):
        url, content = self.search_indeed(job, location)
        total_pages = self.get_total_number_of_jobs(content)

        self.search_jobs(url, job, location, total_pages)


    def search_indeed(self, job, location):
        url = self.base_url + "jobs?q={0}&l={1}".format(job, location)
        content = self.get_content(url)
        return url, content


    def get_total_number_of_jobs(self, content):
        soup = BeautifulSoup(content, "lxml")
        search_count = soup.find(id="searchCount").text
        search_count = re.search("\d+$", search_count)
        if not search_count:
            return None

        search_count = int(search_count.group(0))
        total_pages = search_count / 10
        return total_pages        


    def search_jobs(self, url, search_job, search_location, total_pages):
        for page in range(1, total_pages+1):
            print("%s / %s" % (str(page), str(total_pages)))
            content = self.get_content(url + "&sort=date&start=" + str(page * 10))
            soup = BeautifulSoup(content, "lxml")

            results_td = soup.find("td", id="resultsCol")
            assert results_td != None
            page_rows = results_td.find_all("div", class_="row")
            assert page_rows != None

            try:
                for job in page_rows:
                    job_anchor_tag = job.find("a")
                    job_url = job_anchor_tag["href"]
                    job_id = job["id"]
                    job_location = job.find(class_="location").text
                    job_title = job_anchor_tag["title"].encode("utf-8").decode("ascii", "ignore")
                    job_contents = self.__extract_job_post_contents(self.base_url + job_url)
                    useful_words = self.__sanitize_job_summary(job_contents)
                    keyword_count = sum([1 if f in self.keywords else 0 for f in useful_words])
                    self.db.insert(job_id, job_title, job_url, search_job, search_location, job_location, keyword_count)                    
                    time.sleep(2)


            except Exception as e:
                print(e, job_url)

        print("Done")
        self.db.close()
        

    def __extract_job_post_contents(self, url):
        content = self.get_content(url)
        soup = BeautifulSoup(content, "lxml")
        
        texts = soup.findAll(text=True)
        visible = filter(self.__visible_text, texts)
        visible = [f.strip() for f in visible if f]
        visible = " ".join(visible)
        return visible

    # https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
    def __visible_text(self, element):
        ascii = element.encode("utf-8").decode("ascii", "ignore").strip()
        if not ascii:
            return False
        if element.parent.name in ["style", "script", "[document]", "head", "title"]:
            return False
        elif re.match("<!---.*-->", ascii):
            return False
        return True

        
     
    def __sanitize_job_summary(self, summary):
        summary = summary.encode("utf-8").lower().split()
        stop_words = set(stopwords.words("english"))
        summary = [f for f in summary if not f in stop_words]
        return list(set(summary))


    def __get_keywords(self):
        fileObj = open(self.keywords_filename, "r")
        keywords = fileObj.read().split("\n")
        fileObj.close()
        keywords = [f.lower() for f in keywords if f]
        return set(keywords)
        
 

a = IndeedCrawler(keywords)
content = a.search("Software Developer", "Beaverton, OR")
