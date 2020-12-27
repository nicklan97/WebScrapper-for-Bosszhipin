from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import re
import time
import pymongo


def getHTML(url, proxy_option=False):
    if proxy_option == False:
        driver = webdriver.Chrome(ChromeDriverManager().install())
    else:
        PROXY = "192.168.50.35:24000"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % PROXY)
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(url)
    time.sleep(15)
    html = driver.page_source
    driver.quit()
    return html


def getdict(html):
    page = BeautifulSoup(html, 'html.parser')
    primary = page.find('div', class_='info-primary')
    name = primary.find('div', class_='name').find('h1').text
    salary = primary.find('div', class_='name').find('span').text
    location = primary.find('a', class_='text-city').text
    experience = str(primary.find('p')).split('<em class="dolt"></em>')[1]
    education = re.search('</em>(.+?)</p>', str(primary.find('p'))).group(1).split('</em>')[1]
    tags = ','.join([k.text for k in primary.find('div', class_='job-tags').find_all('span')])
    description = page.find('div', class_='job-sec').find('div',
                                                          class_='text').text.replace('\n', '')
    company_info = page.find('div', class_='sider-company')
    company_name = company_info.find_all('a')[1].text.replace('\n', '').replace(' ', '')
    company_stage = company_info.find_all('p')[1].text
    company_size = company_info.find_all('p')[2].text
    company_industry = company_info.find_all('p')[3].text
    job_id = re.search('targetId:(.+?)\n', str(page.find('head').find_all('script')
                                               [2])).group(1).replace(" '", '').replace("'", '')
    dictionary = {'job_id': job_id, 'name': name, 'location': location, 'salary': salary, 'industry': company_industry, 'description': description,
                  'company': company_name, 'tags': tags, 'size': company_size, 'experience': experience, 'education': education, 'stage': company_stage}
    return dictionary


def insertdata(dictionary):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    Boss = myclient["boss"]
    mycol = Boss["detail"]
    mycol.update_one({'job_id': dictionary['job_id']}, {'$set': dictionary}, True)


if __name__ == '__main__':
    import sys
    import os
    url = sys.argv[1]
    proxy_option = sys.argv[2]
    html = getHTML(url, proxy_option)
    dictionary = getdict(html)
    insertdata(dictionary)
    print('scrapped and stored!')
