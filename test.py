from database import DB_Manager

db = DB_Manager()

def insert_tests():
    db.insert_tech("Python1")
    db.insert_tech("Python2")
    db.insert_tech("Python3")
    db.insert_tech("Python4")
    db.insert_tech("Python5")

    db.insert_job("1", "Tester1", "1", "1", "1", "1")
    db.insert_job("1", "Tester2", "1", "1", "1", "1")
    db.insert_job("1", "Tester3", "1", "1", "1", "1")
    db.insert_job("1", "Tester4", "1", "1", "1", "1")

    db.insert_keyword("Keyword1")
    db.insert_keyword("Keyword2")
    db.insert_keyword("Keyword3")
    db.insert_keyword("Keyword4")


    db.insert_jobs_tech("1", "1")
    db.insert_jobs_tech("2", "2")
    db.insert_jobs_tech("3", "1")


def query_test():
    rows = db.get_all_tech()
    print(rows)


query_test()
db.close()
