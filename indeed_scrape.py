from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import Comment
import re
from database import DB_Manager
from nltk.corpus import stopwords
import os
import time

class IndeedCrawler(object):
    def __init__(self):
        self.base_url = "https://www.indeed.com/"
        self.db = DB_Manager()
        self.stop_words = set(stopwords.words("english"))
        self.driver_indeed = webdriver.Firefox()
        self.driver_job_post = webdriver.Firefox()

    def search(self, job, location):
        total_pages = self.get_total_number_of_jobs(job, location)
        self.search_jobs(job, location, total_pages)


    def get_total_number_of_jobs(self, job, location):
        url = self.base_url + "jobs?q={0}&1={1}".format(job, location)
        self.driver_indeed.get(url)
        search_count = self.driver_indeed.find_element_by_id("searchCount").text
        search_count = re.search("\d+$", search_count)
        if not search_count:
            return None
        search_count = int(search_count.group(0))
        total_pages = search_count / 10
        return total_pages

    def search_jobs(self, job, location, total_pages):
        base_url = self.base_url + "jobs?q={0}&l={1}".format(job, location)
        for page in range(1, total_pages + 1):
            print("%s / %s" % (str(page), str(total_pages)))
            url = base_url + "&sort=date&start=" + str(page * 10)
            self.driver_indeed.get(url)

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
        self.db.close()


    def get_job_content(self, url):
        self.driver_job_post.get(url)
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

print("Done")
