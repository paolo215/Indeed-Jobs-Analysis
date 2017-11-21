from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import Comment
import re
from database import DB_Manager
from nltk.corpus import stopwords
import time

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

        # List of stop words. They are words which
        # do not contain any important significance to be used
        # in search queries.
        self.stop_words = set(stopwords.words("english"))

        # Using two drivers:
        # One is used to move through pages of post listings
        # Other one is used for going to the job url
        # and attempts to scrape readable text
        self.driver_indeed = webdriver.Firefox()
        self.driver_job_post = webdriver.Firefox()

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
        self.driver_indeed.get(url)

        # Find #searchCount id
        search_count = self.driver_indeed.find_element_by_id("searchCount").text

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
            self.driver_indeed.get(url)
            self.driver_indeed.execute_script("window.alert = function () {};")

            # Find search results
            # Indeed is using one big table to organize their site.
            # #resultsCol id contains all the job posts
            # Inside of it contains rows where each row is a job post
            results_td = self.driver_indeed.find_element_by_id("resultsCol")
            page_rows = results_td.find_elements_by_class_name("row")

            try:
                for row in page_rows:
                    job_anchor_tag = row.find_element_by_tag_name("a")
                    job_title = job_anchor_tag.text
                    job_title = ''.join(f for f in job_title if f.isalnum() or f == " ")

                    job_url = job_anchor_tag.get_attribute("href")
                    job_id = row.get_attribute("id")
                    job_location = row.find_element_by_class_name("location").text
                    job_company = row.find_element_by_class_name("company").text

                    if job_company == "Indeed Prime":
                        continue

                    job_content = self.get_job_content(job_url)
                    keywords = self.__sanitize_job_summary(job_content)

                    job_row_id = self.db.insert_job(job_id, job_title, job_url, job, location, job_location, job_company)
                    if job_row_id != -1:
                        for word in keywords:
                            tech_id = self.db.insert_or_update_keyword(word)
                            is_recognized = self.db.does_exists_in_tech_table(word)
                            if is_recognized and tech_id != -1:
                                self.db.insert_jobs_tech(job_id, tech_id)

                    time.sleep(2)
            except Exception as e:
                print(job_url, e)

        print("Done")


    def get_job_content(self, url):
        self.driver_job_post.get(url)
        self.driver_job_post.execute_script("window.alert = function () {};")
        soup = BeautifulSoup(self.driver_indeed.page_source, "lxml")

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
        elif isinstance(element, Comment):
            return False
        elif re.match("http://", ascii):
            return False
        return True

    def __sanitize_job_summary(self, summary):
        words = summary.encode("utf-8").lower().split()
        sanitized_words = []

        for i in range(len(words)):
            if not words[i] in self.stop_words:
                words[i] = re.sub(r"[\W\'\"\)\(,:]", "", words[i])
                if words[i]:
                    sanitized_words.append(words[i])

        return list(set(sanitized_words))

    def close(self):
        self.driver_indeed.close()


a = IndeedCrawler()
a.search("Software Developer", "Beaverton, OR")
a.search("Python", "Beaverton, OR")
a.search("Java", "Beaverton, OR")
a.close()

print("Done")
