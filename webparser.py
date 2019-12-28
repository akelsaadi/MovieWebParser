from bs4 import BeautifulSoup
import cfscrape
import pysftp
import sys
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def do_scraping(link):
    scraper = cfscrape.create_scraper()
    original_content = scraper.get(link)
    soup_content = BeautifulSoup(original_content.content)
    return(soup_content)


#Gets the links on the pages
def get_links(content):
    movies_div = content.find("div", {"id": "scroll"})
    single_movies = movies_div.find_all("article", {"class":"poster"})
    for single_movie in single_movies:
        for links in single_movie.find_all("a", {"title":"”مشاهدة"}):
            movie_link = (links.get('href'))
            print(movie_link)
            movie_name = get_movie_name(movie_link)
            #print("Name:" + movie_name)
            #get_imdb_info(movie_name)
            sftp_link = get_watching_links(movie_link)
            if sftp_link is not None:
                #print (sftp_link)
                #url = 'https://bg.stream.fushaar.com/media/29077/29077.mp4'
                print("getting movie...")
                urllib.request.urlretrieve(sftp_link, 'C:/Users/key/Downloads/movies/' + movie_name + '.mp4')
                print("putting movie...")
                put_file_sftp(movie_name)


#gets the last page
def get_last_page():
    #Get number of pages and go through the pages
    web_content = do_scraping("https://www.fushaar.com/")
    page_div = web_content.find("div", {"class":"pagination"})
    single_pages = page_div.find_all("a")
    last_page_href = (single_pages[-1].get('href'))
    last_page = last_page_href.split("/")
    last_page_number = last_page[-2]
    return last_page_number

def get_watching_links(link):
    link_number = 0
    current_content = do_scraping(link)
    separate_divs = current_content.find_all("a", {"class":"remodal-cancelZ"})
    if len(separate_divs) == 0:
        separate_divs = current_content.find_all("a", {"class":"watch-hd"})
    for watch_links in separate_divs:
        watching_link = watch_links.get('href')
        if ".mp4" in watching_link:
        #link_number = link_number + 1
            print ("link " + str(link_number) + ": " + watching_link)
            return (watching_link)
            break


def go_to_page():
    last_number = get_last_page()
    page_count = 0
    for i in range(int(last_number)):
        page_count = page_count + 1
        soup = do_scraping("http://www.fushaar.com/page/"+str(page_count))
        get_links(soup)

def get_movie_name(url):
    movie_link = do_scraping(url)
    title_header = movie_link.find("header",{"id":"single"})
    title_span = title_header.find_all('span')
    return (title_span[1].text)




def put_file_sftp(mov_name):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    srv = pysftp.Connection(host="78.46.95.40", username="alimov",password="alimov", cnopts=cnopts, default_path='/home/alimov')
    srv.put('C:/Users/key/Downloads/movies/' + mov_name + '.mp4')
    data = srv.listdir()
    srv.close()





#url = 'https://bg.stream.fushaar.com/media/29077/29077.mp4'
#urllib.request.urlretrieve(url, '/directory/'+movie_name+'.mp4')
if __name__ == "__main__":
    go_to_page()
# loop around all pages
# last page is the end of loop
# call above to read movies in every iteration
#srv = pysftp.Connection(host="78.46.95.40", username="root",
#password="SDert427fgsZvh")
