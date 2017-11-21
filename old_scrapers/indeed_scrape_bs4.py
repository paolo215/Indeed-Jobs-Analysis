import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from nltk.corpus import stopwords
from fake_useragent import UserAgent
import os
import re
import time
from database import DB_Manager


class IndeedCrawler(object):
    def __init__(self):
        self.base_url = "https://www.indeed.com/"
        self.db = DB_Manager()
        self.user_agent = UserAgent()
        self.headers = {"headers": self.user_agent.chrome}
        self.stop_words = set(stopwords.words("english"))
        self.headers["Accept-Encoding"] = "identity"
        self.keywords = self.__get_techs()


    def get_content(self, url):
        return requests.get(url, self.headers).content


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
                    job_company = job.find(class_="company").text

                    if job_company == "Indeed Prime":
                        continue

                    job_title = job_anchor_tag["title"].encode("utf-8").decode("ascii", "ignore")
                    job_content = self.extract_job_post_content(self.base_url + job_url)
                    useful_words = self.__sanitize_job_summary(job_content)
                    print(self.db.insert_job(job_id, job_title, job_url, search_job, search_location, job_location))
                    for word in useful_words:
                        tech_id = self.db.insert_or_update_keyword(word)
                        is_recognized = self.db.does_exists_in_tech_table(word)
                        if is_recognized and tech_id != -1:
                            self.db.insert_jobs_tech(job_id, tech_id)


                    print(job_url)
                    keyword_count = sum([1 if f in self.keywords else 0 for f in useful_words])

                    time.sleep(2)
   
            except Exception as e:
                print(e, job_title, job_url)


        print("Done")
        self.db.close()
        

    def extract_job_post_content(self, url):
        content = self.get_content(url)
        soup = BeautifulSoup(content, "lxml")
        
        texts = soup.findAll(text=True)
        visible = filter(self.__visible_text, texts)
        visible = [f.strip() for f in visible if f]
        visible = " ".join(visible)
        print(visible.encode("utf-8").decode("ascii", "ignore"))
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
                sanitized_words.append(words[i])
        
        return list(set(sanitized_words))


    def __get_techs(self):
        rows = self.db.get_all_tech()
        return rows

 

a = IndeedCrawler()
# content = a.search("Software Developer", "Beaverton, OR")
# a.extract_job_post_content("http://www.vanderhouwen.com/job-postings/sqa-engineer/")
a.extract_job_post_content("https://ibegin.tcs.com/iBegin/jobs/114603J")
