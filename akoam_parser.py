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
import background
import os
from threading import Thread
from selenium.webdriver.chrome.options import Options
from queue import Queue
import datetime

directory_name = '/Users/alielsaadi/downloads/'


def do_scraping(link):
    scraper = cfscrape.create_scraper()
    original_content = scraper.get(link)
    soup_content = BeautifulSoup(original_content.content)
    return soup_content


def get_menu_link():
    web_content = do_scraping('https://w5.akoam.net/')
    menu_div = web_content.find("div", {"class": "main_menu"})
    page_a_tag = menu_div.find_all("a")
    page_h_tag = menu_div.find_all("h2")
    for page_ref_tag in page_a_tag:
        category_link = page_ref_tag.get("href")
        get_page_tiles(category_link)

    return None


def go_to_menu_item(menu_link, movie_section):
    get_page_tiles(menu_link, movie_section)


def get_page_tiles(category_link, movie_section):
    web_content = do_scraping(category_link)
    # print (web_content)
    subject_boxes = web_content.find_all("div", {"class": "subject_box shape"})
    threads = []
    q = Queue(maxsize=0)
    num_threads = min(5, len(subject_boxes))
    for i in range(len(subject_boxes)):
        q.put((i, subject_boxes[i]))
    for i in range(num_threads):
        print("starting thread" + str(i))
        worker = Thread(target=use_page_tiles, args=(q, web_content, movie_section))
        worker.setDaemon(True)
        worker.start()
    q.join()
    print ("All tasks Complete")


def use_page_tiles(q, web_content, movie_section):
    while not q.empty():
        work = q.get()
        subject_box_a_tag = work[1].find_all("a")
        # print (subject_box_a_tag)
        page_ref_link = subject_box_a_tag[0].get('href')
        # process = Thread(target = get_movie_link, args = [page_ref_link])
        movie_link = get_movie_link(page_ref_link)
        movie_name = get_movie_name(page_ref_link)
        movie_link = get_aatfal_link(movie_link)
        movie_download_link = get_movie_download_link(movie_link)
        if movie_download_link != "":
            if file_exists_sftp(movie_name):
                try:
                    if pathlib.Path(directory_name + movie_name + '.mkv').exists():
                        print("File Exists")
                    else:
                        print("getting movie... " + movie_name)
                        urllib.request.urlretrieve(movie_download_link, directory_name + movie_name + '.mkv')
                        print("putting movie... " + movie_name)
                        put_file_sftp(movie_name, movie_section)
                        if os.path.exists(directory_name + movie_name + '.mkv'):
                            os.remove(directory_name + movie_name + '.mkv')
                        else:
                            pass

                except:
                    pass
        q.task_done()
    return True
    # next_page_class = web_content.find("a",{"class":"next"})
    # next_page_link = next_page_class.get('href')
    # if next_page_link != '':
    #    get_page_tiles(next_page_link)


def get_movie_name(movie_link):
    web_content = do_scraping(movie_link)
    final_word = ""
    div_class = web_content.find("span", {"class": "sub_file_title"})
    h1 = div_class.text
    h2 = div_class.text.split('.')
    for words in h2[:-5]:
         final_word = final_word + " " + words
    return (final_word)


def get_movie_download_link(aatfal_link):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(executable_path=r"/Users/alielsaadi/pycharmprojects/webparser2/chromedriver",
                               chrome_options=chrome_options)
    browser.get(aatfal_link)
    time.sleep(7)
    try:
        aatfal_link_href = browser.find_element_by_xpath('//div[@id="timerHolder"]')
        aatfal_link = aatfal_link_href.find_element_by_css_selector('a').get_attribute('href')
    except:
        pass

    return (aatfal_link)
    browser.close()


def get_movie_link(movie_link):
    web_content = do_scraping(movie_link)
    button_class = web_content.find("a", {"class": "download_btn"})
    button_link = button_class.get("href")
    return button_link


def get_aatfal_link(akoam_movie_link):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(executable_path=r"/Users/alielsaadi/pycharmprojects/webparser2/chromedriver",
                               chrome_options=chrome_options)

    browser.get(akoam_movie_link)
    try:
        akoam_link_href = browser.find_element_by_xpath('//div[@ng-if="link.route"]')
        akoam_link = akoam_link_href.find_element_by_css_selector('a').get_attribute('href')
    except:
        pass
    return (akoam_link)
    browser.close()


def file_exists_sftp(mov_name):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    srv = pysftp.Connection(host="78.46.95.40", username="alimov", password="alimov", cnopts=cnopts)

def put_file_sftp(mov_name, movie_section):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    current_date = datetime.date.today().strftime("%m.%d.%Y")
    current_date = str(current_date)
    srv = pysftp.Connection(host="78.46.95.40", username="alimov", password="alimov", cnopts=cnopts,
                            default_path='/home/alimov')
    final_path = str('/home/alimov/' + current_date + '/' + movie_section)
    print (final_path)
    try:
        srv.chdir(final_path)
    except IOError:
        srv.mkdir('/home/alimov/' + current_date)
        srv.mkdir('/home/alimov/' + current_date + '/' + movie_section)
    srv.cd('/home/alimov/'+ current_date + '/' + movie_section)
    srv.put(directory_name + mov_name + '.mkv')
    data = srv.listdir()
    srv.close()


# get_menu_link()


# correct path: C:/Users/key/Downloads/movies/
# print(get_menu_link())
# get_page_tiles("https://w5.akoam.net/cat/156/%D8%A7%D9%84%D8%A3%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%84%D8%A7%D8%AC%D9%86%D8%A8%D9%8A%D8%A9")
# get_movie_link("https://w5.akoam.net/180496/%D9%81%D9%8A%D9%84%D9%85-Herbie-Fully-Loaded-2005-%D9%85%D8%AF%D8%A8%D9%84%D8%AC-%D9%84%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9")
# get_movie_download_link("https://w5.akoam.net/download/4f0d13487dd0/Apparition-2019-1080p-WEB-DL-akoam-net-mkv")
# get_movie_name("https://w5.akoam.net/180489/%D9%81%D9%8A%D9%84%D9%85-The-Bad-Guys-Reign-of-Chaos-2019-%D9%85%D8%AA%D8%B1%D8%AC%D9%85")
if __name__ == "__main__":
    go_to_menu_item(
        "https://w5.akoam.net/cat/155/%D8%A7%D9%84%D8%A3%D9%81%D9%84%D8%A7%D9%85-%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9", "Arabic")
    #get_movie_name(
    #    "https://w5.akoam.net/178994/%D9%81%D9%8A%D9%84%D9%85-%D9%82%D8%A8%D9%84-%D9%85%D8%A7-%D9%8A%D9%81%D9%88%D8%AA-%D8%A7%D9%84%D9%81%D9%88%D8%AA")
    #put_file_sftp("jewlery_iamge.png", "Arabic")