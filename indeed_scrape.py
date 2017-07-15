import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import os
import re
import sqlite3

dbname = "indeed_jobs.sqlite"
keywords = "keywords.txt"

class IndeedCrawler(object):
    def __init__(self, keywords_filename, db_filename):
        self.keywords_filename = keywords_filename
        self.db_filename = db_filename
        self.base_url = "https://www.indeed.com/"
        self.keywords = self.__get_keywords()

    def get_content(self, url):
        return requests.get(url).content

    def search_indeed(self, job, location):
        url = self.base_url + "jobs?q={0}&l={1}".format(job, location)
        content = self.get_content(url)
        return content


    def search_jobs(self, content):
        soup = BeautifulSoup(content, "lxml")
        results_td = soup.find("td", id="resultsCol")
        assert results_td != None
        page_rows = results_td.find_all("div", class_="row")
        assert page_rows != None

        for job in page_rows:
            job_anchor_tag = job.find("a")
            job_url = job_anchor_tag["href"]
            job_id = job["id"]
            job_title = job_anchor_tag["title"]
            job_contents = self.__extract_job_post_contents(self.base_url + job_url)
            useful_words = self.__sanitize_job_summary(job_contents)

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
        contents = fileObj.read().split("\n")
        fileObj.close()
        contents = [f.lower() for f in contents if f]
        return contents
        
 

a = IndeedCrawler()
content = a.search_indeed("Software Developer", "Beaverton, OR")
a.search_jobs(content)
