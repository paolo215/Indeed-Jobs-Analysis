import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import os
import re
import sqlite3

dbname = "indeed_jobs.sqlite"


class IndeedCrawler(object):
    def __init__(self):
        self.base_url = "https://www.indeed.com/"

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
            job_url = job.find("a")["href"]
            if re.match("^/rc/", job_url) != None or re.match("/pagead/", job_url) != None:
                continue
            job_id = job["id"]
            job_title, job_summary = self.__extract_indeed_job_contents(self.base_url + job_url)
            useful_words = self.__sanitize_job_summary(job_summary)

        

    def __extract_indeed_job_contents(self, url):
        content = self.get_content(url)
        soup = BeautifulSoup(content, "lxml")
        job_title = None
        job_summary = None
        try:
            job_content = soup.find(id="job-content").td
            job_title = job_content.find(class_="jobtitle").text
            job_summary = job_content.find(id="job_summary").find_all("p")
            job_summary = [f.text for f in job_summary]
            job_summary = " ".join(job_summary)
        except Exception as e:
            print(e, url)


        return job_title, job_summary

     
    def __sanitize_job_summary(self, summary):
        summary = summary.encode("utf-8").lower().split()
        stop_words = set(stopwords.words("english"))
        summary = [f for f in summary if not f in stop_words]
        return list(set(summary))

 

a = IndeedCrawler()
content = a.search_indeed("Software Developer", "Beaverton, OR")
a.search_jobs(content)
