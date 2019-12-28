from bs4 import BeautifulSoup
import cfscrape
import pysftp
import sys
import urllib.request
import ssl
import pathlib
import urllib3
import json
from selenium import webdriver
import pandas as pd
import requests
import time
from selenium.webdriver.chrome.options import Options


def do_scraping(link):
    scraper = cfscrape.create_scraper()
    original_content = scraper.get(link)
    soup_content = BeautifulSoup(original_content.content)
    return soup_content


def get_menu_link():
    web_content = do_scraping('https://w5.akoam.net/')
    menu_div = web_content.find("div", {"class":"main_menu"})
    page_a_tag = menu_div.find_all("a")
    page_h_tag = menu_div.find_all("h2")
    for page_ref_tag in page_a_tag:
        category_link = page_ref_tag.get("href")
        get_page_tiles(category_link)

    return None

def go_to_menu_item(menu_link):
    get_page_tiles(menu_link)


def get_page_tiles(category_link):
    web_content = do_scraping(category_link)
    #print (web_content)
    subject_boxes = web_content.find_all("div", {"class":"subject_box shape"})
    for subject_box in subject_boxes:
        subject_box_a_tag = subject_box.find_all("a")
        #print (subject_box_a_tag)
        for page_ref_tag in subject_box_a_tag:
            page_ref_link = page_ref_tag.get('href')
            movie_link = get_movie_link(page_ref_link)
            movie_name = get_movie_name(page_ref_link)
            movie_link = get_aatfal_link(movie_link)
            movie_download_link = get_movie_download_link(movie_link)
            if movie_download_link != "":
                try:
                    if pathlib.Path('/Users/alielsaadi/downloads/' + movie_name +'.mkv').exists():
                        print("File Exists")
                    else:
                        print("getting movie... " + movie_name)
                        urllib.request.urlretrieve(movie_download_link, '/Users/alielsaadi/downloads/' + movie_name + '.mkv')
                        print("putting movie... " + movie_name)
                        put_file_sftp(movie_name)
                except:
                    pass
    next_page_class = web_content.find("a",{"class":"next"})
    next_page_link = next_page_class.get('href')
    if next_page_link != '':
        get_page_tiles(next_page_link)




def get_movie_name(movie_link):
    web_content = do_scraping(movie_link)
    div_class = web_content.find("div", {"class":"sub_title"})
    h1 = div_class.find("h1")
    return (h1.text)


def get_movie_download_link (aatfal_link):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(executable_path=r"/Users/alielsaadi/pycharmprojects/webparser2/chromedriver", chrome_options = chrome_options)
    browser.get(aatfal_link)
    time.sleep(7)
    aatfal_link_href = browser.find_element_by_xpath('//div[@id="timerHolder"]')
    aatfal_link = aatfal_link_href.find_element_by_css_selector('a').get_attribute('href')
    return (aatfal_link)
    browser.close()

def get_movie_link (movie_link):
    web_content = do_scraping(movie_link)
    button_class = web_content.find("a", {"class":"download_btn"})
    button_link = button_class.get("href")
    return button_link


def get_aatfal_link(akoam_movie_link):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(executable_path=r"/Users/alielsaadi/pycharmprojects/webparser2/chromedriver", chrome_options = chrome_options)
    browser.get(akoam_movie_link)

    akoam_link_href = browser.find_element_by_xpath('//div[@ng-if="link.route"]')
    akoam_link = akoam_link_href.find_element_by_css_selector('a').get_attribute('href')
    return(akoam_link)
    browser.close()


def put_file_sftp(mov_name):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    srv = pysftp.Connection(host="78.46.95.40", username="alimov",password="alimov", cnopts=cnopts, default_path='/home/alimov')
    srv.put('/Users/alielsaadi/downloads/' + mov_name + '.mkv')
    data = srv.listdir()
    srv.close()


#get_menu_link()


#correct path: C:/Users/key/Downloads/movies/
#print(get_menu_link())
#get_page_tiles("https://w5.akoam.net/cat/156/%D8%A7%D9%84%D8%A3%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%84%D8%A7%D8%AC%D9%86%D8%A8%D9%8A%D8%A9")
#get_movie_link("https://w5.akoam.net/180496/%D9%81%D9%8A%D9%84%D9%85-Herbie-Fully-Loaded-2005-%D9%85%D8%AF%D8%A8%D9%84%D8%AC-%D9%84%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9")
#get_movie_download_link("https://w5.akoam.net/download/4f0d13487dd0/Apparition-2019-1080p-WEB-DL-akoam-net-mkv")
#get_movie_name("https://w5.akoam.net/180489/%D9%81%D9%8A%D9%84%D9%85-The-Bad-Guys-Reign-of-Chaos-2019-%D9%85%D8%AA%D8%B1%D8%AC%D9%85")
if __name__ == "__main__":
    go_to_menu_item("https://w5.akoam.net/cat/155/%D8%A7%D9%84%D8%A3%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9")