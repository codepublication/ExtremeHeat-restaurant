from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import time
import csv
import os
import re
import pandas as pd
import sys
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

class YelpCrawler:

    def __init__(self, city, state):
        # def __init__(self):
        self.CITY_NAME = city
        self.STATE_NAME = state
        self.NEIGHBORHOOD_LIST_FILE_NAME = "data/yelp_neighborhood_{}.csv".format(self.CITY_NAME)
        # self.NEIGHBORHOOD_LIST_FILE_NAME = "data/cities.csv"

        options = webdriver.ChromeOptions()
        options.add_argument("--verbose")
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("--window-size=1920, 1200")
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)

        driver.set_page_load_timeout(10000)

        # self.browser = webdriver.Chrome()
        self.browser = driver
        self.locations_list = []
        self.location_id = 0  # row of location in file to start crawling (starting from 0)
        self.current_page = 0
        self.end_of_results = False

    def iterate_crawl(self, current_page):
        self.current_page = current_page
        print("crawling {}, page={}".format(self.CITY_NAME, self.current_page))
        self.crawl_page()

    def url_encode(self, loc_str):
        str_list = loc_str.split(" ")
        if len(str_list) == 1:
            return loc_str
        else:
            encoded_str = ""
            for x in range(len(str_list)):
                if x is len(str_list) - 1:
                    encoded_str += str_list[x]
                else:
                    encoded_str += str_list[x] + "_"
            return encoded_str

    def build_url(self):
        url = "https://www.yelp.com/search?"
        if BUSINESS_TYPE is not "":
            url += "find_desc={}".format(BUSINESS_TYPE)
        url += "&start={}".format(self.current_page * RESULTS_PER_PAGE)
        url += "&find_loc={}".format(self.CITY_NAME)
        url += "%2C+{}".format(self.STATE_NAME)
        return url

    def get_page_number(self):
        self.browser.get(self.build_url())
        self.browser.implicitly_wait(10)  # 隐式等待，最长等20秒
        total_mass = self.browser.find_element(By.XPATH, ".//*[contains(text(),'1 of')]").text
        # total_page_str = ' '.join(map(str, rest_category[-3]))
        total_page_number = int(total_mass[-2:])
        print("total_page_number", total_page_number)
        return total_page_number  # css-1aq64zd

    def crawl_page(self):
        self.browser.get(self.build_url())
        self.browser.implicitly_wait(10)  # 隐式等待，最长等20秒

        yelp_biz = []
        yelp_biz_urls = []
        # collect all urls to business page
        try:
            yelp_titles = self.browser.find_elements(By.CSS_SELECTOR, 'h3.css-1agk4wl')
            for title in yelp_titles:
                pp2 = title.find_element(By.CLASS_NAME, 'css-1egxyvc')
                if pp2.text[0].isdigit() == True:
                    #print(pp2.text)
                    pp3 = pp2.find_element(By.TAG_NAME, 'a').get_property('href')
                    yelp_biz_urls.append(pp3)
                else:
                    pass
        except:
            pass

        print("{} business links found on page".format(len(yelp_biz_urls)))
        if len(yelp_biz_urls) == 0:
            self.end_of_results = True

        for yelp_biz_url in yelp_biz_urls:
            biz_obj = {}
            self.browser.get(yelp_biz_url)
            biz_obj["id"] = yelp_biz_urls.index(yelp_biz_url) + 1
            try:
                biz_obj["name"] = self.browser.find_element(By.XPATH, '//h1[@class="css-1se8maq"]').text
                time.sleep(2)
            except:
                biz_obj["name"] = ""
            try:
                biz_obj["address"] = self.browser.find_element(By.XPATH, '//p[@class=" css-qyp8bo"]').text
                time.sleep(2)
            except:
                biz_obj["address"] = ""
            yelp_biz.append(biz_obj)

        df = pd.DataFrame(yelp_biz,
                          columns=["id", "name", "address"])
        try:
            df.to_csv("data/{}_{}.csv".format(self.CITY_NAME, self.STATE_NAME), mode='a', header=False, index=False)
        except Exception as e:
            print("Exception", e)
        time.sleep(2)

city_msa = pd.read_csv('E:\scrapy\city_MSA.csv')
print(city_msa)


for i in [430]:
    CITY_NAME = city_msa.iloc[i]['CITY']
    STATE_NAME = city_msa.iloc[i]['State']
    BUSINESS_TYPE = 'Delivery+Restaurants'
    RESULTS_PER_PAGE = 10
    STARTING_PAGE_TO_CRAWL = 0  # first page is id zero
    print("crawling city" ,i,CITY_NAME,",",STATE_NAME)
    yc = YelpCrawler(CITY_NAME,STATE_NAME)
    #total_p = yc.get_page_number()
    total_p =16
    for j in list(range(2,total_p)):
        yc.iterate_crawl(j)
    print("Done for {}".format(CITY_NAME))
