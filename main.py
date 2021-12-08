#/bin/python3

import requests
import time
import csv
import os.path
from os import mkdir as os_mkdir
from os import getcwd as os_getcwd
from matplotlib import pyplot as plt
import datetime
import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup

def create_folder_structure():
    #checks if the data/$WEEKDAY folders exists
    #if not, creates them
    if os.path.isdir('data') == True:
        print('data folder exists already. skipping...')
    else:
        os_mkdir('data')
    if os.path.isdir('output') == True:
        print('output folder exists already. skipping...')
    else:
        os_mkdir('output')
    weekdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
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
    current_path = os_getcwd()
    driver_path = str(current_path + '/chromedriver_mac')
    driver = webdriver.Chrome(driver_path, options=options)
    
    #render the webpage headless and parse the source to beautiful soup
    driver.get(page_string)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    #gets the utilization string from the homepage and extracts the number
    people_count_text = soup.select_one("div[class=status_text]").text
    people_count_integer = people_count_text.strip().split(' ')[0]
    current_time = datetime.datetime.now().strftime("%H%M")
    
    result = [current_time, people_count_integer]
    
    return result
    
def path_to_current_file(mode):
    #returns the path to daily data-file for using in input and plotting
    #filepath is ./data/$weekday/$date.out if mode == text
    #or ./output/$date if mode == plot
    now = datetime.datetime.now()
    weekday = now.strftime("%a").lower()
    date = now.strftime("%y_%m_%d")
    if mode == "text":
        path_to_file = os.path.join('data',weekday,date)
    elif mode == "plot":
        path_to_file = os.path.join('output',date)
    else:
        print("wrong argument")
    
    return path_to_file
  
def write_to_file(results, path):
    #write the data in a file
    print("Writing to : " + str(path) + " at: " + str(results[0]))
    with open(path, 'a') as file: 
        pars_string = str(results[0]+','+results[1]+'\n')
        file.write(pars_string)
        
def create_output_figure(daily_data, opening, closing, output_fig):
    #creates a figure based on daily data and the opening and closing hours
    #time-format needs to be integer as follows: 9:00 = 900, 23:00 = 2300
    utilization = []
    with open(daily_data, 'r') as util_file:
        reader = csv.reader(util_file)
        for row in reader:
            utilization.append(row)
        
    
    #filter utilization array so that it doesnt show values where b12 is closed
    utilization = list(filter(lambda x: int(x[0])>opening and int(x[0])<closing,utilization))

    time = [x[0] for x in utilization]
    people = [105 - int(x[1]) for x in utilization]
    
    #create a string from the time-values for nicer plotting
    time_string = []
    for timestamp in time: 
        hours   = timestamp[:2]
        minutes = timestamp[-2:]
        time_string.append(str(hours + ':' + minutes))
    
    
    #Plotting
    fig = plt.figure(figsize=[20,10])
    fig.patch.set_facecolor('white')
    ax1 = fig.add_subplot(111)
    ax1.set_title("B12 - Personenanzahl")
    ax1.title.set_fontsize(20)
    ax1.set_ylabel("Personen", fontsize = 20)
    ax1.set_xlabel("Uhrzeit", fontsize = 20)
    ax1.set_yticks(np.arange(0,110,10))
    ax1.set_ylim([0,100])
    ax1.set_xlim([0,80])
    ax1.tick_params(axis='x', labelrotation = 45)
    ax1.plot(time_string, people, 'r', linewidth = 2)
    ax1.plot(time_string, people, 'r', linewidth = 2)
    for label in ax1.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)
    plt.gcf()
    plt.savefig(output_fig)
    plt.close()
        
def go_to_sleep(sleep_timer):
    #waits the specified amount of time
    time.sleep(sleep_timer)
    

def main():
    create_folder_structure()
    while True:
        try:
            b12_results = get_current_peoplecount()
            write_to_file(b12_results, path_to_current_file('text'))      
        except:
            print("something with the webpage was off.. skipping...")
        create_output_figure(path_to_current_file('text'),930, 2200,'today.png')
        create_output_figure(path_to_current_file('text'),930, 2200,path_to_current_file('plot'))
        go_to_sleep(600) #15min * 60s = 900s
    
if __name__ == "__main__":
    main()
