from selenium import webdriver
import re
from database import DB_Manager
from nltk.corpus import stopwords

class IndeedCrawler(object):
    def __init__(self):
        self.base_url = "https://www.indeed.com/"
        self.db = DB_Manager()
        self.stop_words = set(stopwords.words("english"))
        self.driver = webdriver.Firefox()


    def get_content(self, url):
        pass


    def search(self, job, location):
        print(self.get_total_number_of_jobs())
        self.close()


    def get_total_number_of_jobs(self):
        url = self.base_url + "jobs?q={0}&1={1}".format(job, location)
        self.driver.get(url)
        search_count = self.driver.find_element_by_id("searchCount").text
        search_count = re.search("\d+$", search_count)
        if not search_count:
            return None
        search_count = int(search_count.group(0))
        total_pages = search_count / 10
        

    


    def search_jobs(self, url, search_job, search_location, total_pages):
        pass

    def close(self):
        self.driver.close()


a = IndeedCrawler()
a.search("Software Developer", "Beaverton, OR")

print("Done")
