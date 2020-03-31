from selenium import webdriver 
import os playlist_url = 'HERE COMES THE PLAYLIST URL' # youtube playlist url (Format: https://www.youtube.com/playlist?list=X1Y2Z3)

#print(os.path.join('first_part', 'second_part')) 
chromium_path = os.getcwd() + '\data\chromedriver.exe' 
options = webdriver.ChromeOptions() #options.add_argument('--log-level=3') 

#options.add_argument('disable_infobars') 
# Disable chrome message 'chrome is being controlled by automated software'

options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Disable dev mode to suppress error
