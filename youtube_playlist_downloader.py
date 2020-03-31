import os
import time
import requests
import youtube_dl
from bs4 import BeautifulSoup
from selenium import webdriver

from data import config # import custom config
 
def infinite_scroll(driver):    # https://stackoverflow.com/questions/28928068/scroll-down-to-bottom-of-infinite-page-with-phantomjs-in-python/28928684#28928684
    SCROLL_PAUSE_TIME = 1

    # get scroll height
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        # scroll down to bottom
        driver.execute_script('window.scrollTo(0, ' + str(last_height) + ');')

        # wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script('return document.documentElement.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height

def getPlaylistLinks(url):
    
    driver = webdriver.Chrome(executable_path=config.chromium_path, options=config.options)
    driver.get(url)     # open chromium tab and browse to url
    time.sleep(0.05)

    infinite_scroll(driver) # scroll to bottom of page
    sourceCode = driver.page_source # retrieve source code
    soup = BeautifulSoup(sourceCode, 'html.parser') # parse source code with a html parser 
    domain = 'https://www.youtube.com'

    playlist_channel_info = soup.find('div', {'id':'upload-info'})  # scrape general playlist information
    playlist_channel_info = playlist_channel_info.find('a')
    playlist_channel_name = playlist_channel_info.text
    playlist_channel_url = playlist_channel_info.attrs['href']
    
    playlist_title = soup.find('h1', {'id':'title'})
    playlist_title = playlist_title.find('a').text

    playlist_general_information = {
        'channelName': playlist_channel_name,
        'channelUrl': domain + playlist_channel_url,
        'playlistTitle': playlist_title
    }

    # create directory for playlist if not exist
    directory = os.getcwd() + '/output/' + playlist_title + '/text/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = directory + playlist_title + '_full.txt'
    f = open(filename, 'a', encoding='utf-8') # write url and title into txt
    f.truncate(0) # clear file

    title_url_list = [['Video Title', 'Video URL']]
    for link in soup.find_all("a", {"class": "yt-simple-endpoint style-scope ytd-playlist-video-renderer"}):
        url = link.attrs['href']
        
        if url.startswith('/watch?'):            
            cropped_url = url.strip().split('&')[0] # crop playlist url part off
            url = domain + cropped_url
            video_title = link.find('span', {'id':'video-title'})
            title = video_title.attrs['title']
            for r in ((' ','_'), ('/','-'), (',','_')):    # replace strings in playlistnames so result is compatible as file name
                title = title.replace(*r)
            title_url_list.append([title, url])
            f.write(title + '   ' + url + '\n') # write video information to new line in the text file
        else:
            print('URL is not of correct form')
    f.close()

    return title_url_list, playlist_title

def download_video(title_url_list, playlist_title):
    
    # create directories if not existing already
    directory_text = os.getcwd() + '/output/' + playlist_title + '/text/'
    directory_audio = os.getcwd() + '/output/' + playlist_title + '/audio/'  
    directory_video = os.getcwd() + '/output/' + playlist_title + '/video/' 
    directory_archive = os.getcwd() + '/output/' + playlist_title + '/archive/'
    if not os.path.exists(directory_video):
        os.makedirs(directory_video)
    if not os.path.exists(directory_audio):
        os.makedirs(directory_audio)
    if not os.path.exists(directory_text):
        os.makedirs(directory_text)
    if not os.path.exists(directory_archive):
        os.makedirs(directory_archive)

    video_count = len(title_url_list)

    faulty_entries = []
    for idx, val in enumerate(title_url_list[1:]):    # start at second element
        print('\nCurrent Youtube Video = ', val)
        title = val[0]
        url = val[1]
        print('Output Directory: ', directory_audio)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': directory_audio + '/' + title + '.%(ext)s',
            'download_archive': directory_archive + '/'+ title + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print('{} of {} already processed'.format(idx+1, video_count))
        except:
            faulty_entries.append(title_url_list.index(val))
            print("!!!! Error downloading with youtube-dl !!!!")        

    print('Faulty Youtube Videos, (deleted, copyright issues etc.): ', faulty_entries)

    filename = directory_text + playlist_title + '_faulty.txt'  # create text file containing the faulty video list 
    f = open(filename, 'a', encoding='utf-8')
    f.truncate(0) # clear file

    for item in sorted(faulty_entries, reverse=True):  # remove faulty entries from the list containing all playlist video information
        temp = title_url_list[item][0] + '        ' + title_url_list[item][1]
        f.write("%s\n" % temp)  # add faulty video to text file
        del title_url_list[item]    # delete faulty entry from list
    f.close

    filename = directory_text + playlist_title + '_cleaned.txt' # create text file containing only succesfully downloaded playlist entries 
    f = open(filename, 'a', encoding='utf-8')
    f.truncate(0) # clear file

    for item in title_url_list:
        temp = item[0] + '        ' + item[1]
        f.write("%s\n" % temp)
    f.close    

if __name__ == "__main__":
    title_url_list, playlist_title = getPlaylistLinks(config.playlist_url)
    download_video(title_url_list, playlist_title)
