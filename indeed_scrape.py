from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import Comment
from fake_useragent import UserAgent
import re
from database import DB_Manager
from nltk.corpus import stopwords
import time
import requests

class IndeedCrawler(object):
    """
    Scrapes all job postings from Indeed.com
    """
    def __init__(self):
        """
        Initializes IndeedCrawler
        """
        self.base_url = "https://www.indeed.com/"

        # Handles DB interaction
        self.db = DB_Manager()
        self.user_agent = UserAgent()
        self.headers = {"headers": self.user_agent.chrome}
        self.headers["Accept-Encoding"] = "identity"

        # List of stop words. They are words which
        # do not contain any important significance to be used
        # in search queries.
        self.stop_words = set(stopwords.words("english"))

    def get_content(self, url):
        return requests.get(url, self.headers).content

    def search(self, job, location):
        """
        Searches for job listing based on job and location provided and scrapes job listing
        """

        # Get total number of pages
        total_pages = self.get_total_pages(job, location)

        # Scrapes all job posts
        self.search_jobs(job, location, total_pages)


    def get_total_pages(self, job, location):
        """
        Attempts to obtain the total number of pages
        """

        # Set up url and go to the url
        url = self.base_url + "jobs?q={0}&1={1}".format(job, location)
        content = self.get_content(url)

        soup = BeautifulSoup(content, "lxml")

        # Find #searchCount id
        search_count = soup.find(id="searchCount").text

        # Get the total number of jobs
        search_count = re.search("\d+$", search_count)

        # Return if it fails to find the total number of jobs
        if not search_count:
            return None

        # Obtain the value and calculate total number of pages
        search_count = int(search_count.group(0))
        total_pages = search_count / 10

        return total_pages

    def search_jobs(self, job, location, total_pages):
        """
        Goes over the search results and scrapes relevant information.
        """

        # Set up base search query url
        base_url = self.base_url + "jobs?q={0}&l={1}".format(job, location)

        # Iterate through pages
        for page in range(1, total_pages + 1):
            print("%s / %s" % (str(page), str(total_pages)))

            # Using start to traverse through pages instead of clicking
            # Because it's easier?
            url = base_url + "&sort=date&start=" + str(page * 10)
            content = self.get_content(url + "&sort=date&start=" + str(page * 10))
            soup = BeautifulSoup(content, "lxml")


            # Find search results
            # Indeed is using one big table to organize their site.
            # #resultsCol id contains all the job posts
            # Inside of it contains rows where each row is a job post
            results_td = soup.find("td", id="resultsCol")
            page_rows = results_td.find_all("div", class_="row")

            try:
                for row in page_rows:

                    # Extract relevant info
                    job_anchor_tag = row.find("a")
                    job_title = job_anchor_tag["title"]
                    job_title = ''.join(f for f in job_title if f.isalnum() or f == " ")
                    job_url = job_anchor_tag["href"]
                    job_id = row["id"]
                    job_location = row.find(class_="location").text.strip()
                    job_company = row.find(class_="company").text.strip()

                    # Skip Indeed Prime posts
                    if job_company == "Indeed Prime":
                        continue

                    # Extract job summary
                    job_content = row.find(class_="summary").text.strip()
                    job_content = re.sub(r"[\'\"\)\(,:]", "", job_content)

                    # Get keywords
                    keywords = self.__sanitize_job_summary(job_content)

                    # Attempts to insert job to the table
                    job_row_id = self.db.insert_job(job_id, job_title, job_url, job, location, job_location, job_company, job_content)

                    # Check if job has already been added
                    if job_row_id != -1:

                        # Insert keyword to the table
                        for word in keywords:
                            tech_id = self.db.insert_or_update_keyword(word)
                            is_recognized = self.db.does_exists_in_tech_table(word)
                            if is_recognized and tech_id != -1:
                                self.db.insert_jobs_tech(job_id, tech_id)

                    time.sleep(2)
            except Exception as e:
                print(e, job_url)


    def __sanitize_job_summary(self, summary):
        words = summary.encode("utf-8").lower().split()
        sanitized_words = []

        for i in range(len(words)):
            if not words[i] in self.stop_words:
                sanitized_words.append(words[i])

        return list(set(sanitized_words))


    def close(self):
        self.db.close()


a = IndeedCrawler()
a.search("Software Developer", "Beaverton, OR")
a.search("Python", "Beaverton, OR")
a.search("Java", "Beaverton, OR")
a.close()

print("Done")
