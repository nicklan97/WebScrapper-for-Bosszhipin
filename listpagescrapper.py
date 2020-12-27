from bs4 import BeautifulSoup
from selenium import webdriver
import random
from webdriver_manager.chrome import ChromeDriverManager
import pymongo
import time
import math


def getdicts(url, proxy_option=False):

"""
this function is going to take in joblist page url we have base on cityname and jobname
and get a list of dictionaries having the scraped id,location,company,skillset,company_industry
and the detail_url,all stored in lists of length 30(except the last page where there are less than 30 job listed),
so the dicts should look like [dict1,dict2,...,dictn], and dict = {'jobname':xxx,...,detail_url:xxx}.
"""
   if proxy_option == False:
        driver = webdriver.Chrome(ChromeDriverManager().install())
    else:
        PROXY = "192.168.50.35:24000"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % PROXY)
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(url)
    time.sleep(10)
    html = driver.page_source
    dicts = []
    page = BeautifulSoup(html, 'html.parser')
    # get the page number for the list by deviding number of job listed by 30
    numofpage = math.ceil(int(page.find('div', class_='job-tab').get('data-rescount'))/30)

    for i in range(1, numofpage + 1):
        # we already have the html of the first page, we renew html from page 2
        if i > 1:
            html = driver.page_source
            page = BeautifulSoup(html, 'html.parser')
        # scrap name as list
        jobnames = page.find_all('span', class_='job-name')
        job_name_list = [k.find('a').text for k in jobnames]
        # scrap location as list
        jobloc = page.find_all('span', class_='job-area')
        job_area_list = [k.text for k in jobloc]
        # scrap salary as list
        salary = page.find_all('span', class_='red')
        jobsalary_list = [k.text for k in salary]
        # scrap company as list
        company = page.find_all('h3', class_='name')
        company = [k.find('a') for k in company]
        res = []
        for val in company:
            if val != None:
                res.append(val)
        jobcompany_list = [k.text for k in res]
        # scrap industry as list
        industry = page.find_all('a', class_='false-link')
        jobindustry_list = [k.text for k in industry]
        # scrap skillset as list
        skills = page.find_all('div', class_='tags')
        jobskills_list = [k.text.replace('\n', ',') for k in skills]
        # scrap jobid as list
        jid = page.find_all('span', class_='job-name')
        job_id_list = [k.find('a').get('data-jobid') for k in jid]
        # get the detail page url as list
        primary = page.find_all('div', class_='primary-box')
        href = [k.get('href') for k in primary]
        ka = [k.get('ka') for k in primary]
        lid = [k.get('data-lid') for k in primary]
        detail_url = []
        for j in range(0, len(primary)):
            detail_url_list.append(web+href[j]+'?'+'ka='+ka[j]+'&'+'lid='+lid[j])
        # now we make each lists into a list of dictionaries and each dictionary records 1 piece of record
        for k in range(0, len(job_name_list)):
            dicts.append({'id': job_id_list[k], 'name': job_name_list[k], 'location': job_area_list[k], 'salary': jobsalary_list[k],
                          'industry': jobindustry_list[k], 'skills': jobskills_list[k], 'company': jobcompany_list[k], 'detail_url': detail_url_list[k]})
        time.sleep(10)
        # flip page till last page
        if i != numofpage:
            driver.find_element_by_class_name('next').click()
    driver.quit()
    return dicts


def insertdata(dicts):

"""
the function will take the list of dicts returned in last function and insert into
mongodb one by one
"""
   myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    Boss = myclient["boss"]
    mycol = Boss["list"]
    for dict in dicts:
        mycol.update_one({'id': dict['id']}, {'$set': dict}, True)


if __name__ == '__main__':
    import sys
    import os
    url = sys.argv[1]
    proxy_option = sys.argv[2]
    dicts = getdicts(url, proxy_option)
    insertdata(dicts)
    print('scrapped and stored!')
