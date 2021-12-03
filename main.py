#/bin/python3

import requests
import time
import os.path
from os import mkdir as os_mkdir
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup

def create_folder_structure():
    #checks if the data/$WEEKDAY folders exists
    #if not, creates them
    if os.path.isdir('data') == True:
        print('data folder exists already. skipping...')
    else:
        os_mkdir('data')
    weekdays = ['mon', 'tue', 'wen', 'thu', 'fri', 'sat', 'sun']
    for day in weekdays:
        path = os.path.join('data',day)
        if os.path.isdir(path) == True: 
            print(path + ' exists already. skipping...')
        elif os.path.isdir(path) == False: 
            os_mkdir(path)

def get_current_peoplecount():
    #uses the b12 homepage to check the current amount of people training
    #returns people-count as integer
    #returns an array
    #example output for 8:15am with 13 people : [0815,13]
    
    page_string = "http://b12-tuebingen.de/"
    
    #define webdriver options
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome("./chromedriver", options=options)
    
    #render the webpage headless and parse the source to beautiful soup
    driver.get(page_string)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    #gets the utilization string from the homepage and extracts the number
    people_count_text = soup.select_one("div[class=status_text]").text
    people_count_integer = people_count_text.strip().split(' ')[0]
    current_time = datetime.now().strftime("%H%M")
    
    result = [current_time, people_count_integer]
    
    return result
    
def write_to_file(results):
    #write the data in a file
    #filepath is ./data/$weekday/$date.out
    
    now = datetime.now()
    weekday = now.strftime("%a").lower()
    date = now.strftime("%y_%m_%d")
    
    path_to_file = os.path.join('data',weekday,date)
    
    #runs as long as the user or something else breaks it
    print("Writing to : " + str(path_to_file) + " at: " + str(results[0]))
    with open(path_to_file, 'a') as file: 
        pars_string = str(results[0]+','+results[1]+'\n')
        file.write(pars_string)
        
def go_to_sleep(sleep_timer):
    #waits the specified amount of time
    time.sleep(sleep_timer)
    

def main():
    create_folder_structure()
    while True: 
        b12_results = get_current_peoplecount()
        write_to_file(b12_results)
        go_to_sleep(900) #15min * 60s = 900s
    
if __name__ == "__main__":
    main()
