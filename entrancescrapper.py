# import required packeges
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
# create a list that can be fitted into url
citylist = ['beijing', 'shanghai', 'guangzhou', 'shenzhen', 'hangzhou', 'tianjin',
            'xian', 'suzhou', 'wuhan', 'xiamen', 'changsha', 'chengdu', 'zhengzhou',
            'chongqing', 'foshan', 'hefei', 'jinan', 'qingdao', 'nanjing', 'dongguan']
# create empy lists of jobname,relative link,citycode in bosszhipin
name = []
link = []
citycode = []
# loop through all cities we are interested in
for city in citylist:
    # driver setup
    driver = webdriver.Chrome(ChromeDriverManager().install())
    # go to the city page
    driver.get(f'https://www.zhipin.com/{city}/?ka=city-sites-101020100')
    time.sleep(5)
    # get home page source code
    html = driver.page_source
    driver.quit()
    # put the source code into BS for info extraction
    page = BeautifulSoup(html, 'html.parser')
    # extract joblist
    category = page.find_all('div', class_='text')
    # extract name and put it into joblist
    name.extend([k.find('a').text for k in category])
    # extract relative link and extract latter part
    link.extend([k.find('a').get('href')[12:].replace('/', '') for k in category])
    # extract relative link and extract former part as city code
    citycode.append(category[0].find('a').get('href')[1:11])
    # finish scraping for one city
    print(f'{city} scrapped')
# generate 2 csv recording the scrapped information
code = pd.DataFrame({'城市': citylist, '代码': citycode})
code.to_csv('城市代码.csv')
jobs = pd.DataFrame({'职位': name, '链接': link})
jobs.to_csv('职位链接.csv')
