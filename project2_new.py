# -*- coding: utf-8 -*-
"""Untitled11.ipynb


"""

#Project 2

#################Selenium:  The Bored Ape Yacht Club#################

#“[The] Bored Ape Yacht Club […] is a non-fungible token (NFT) collection built on 
#the Ethereum blockchain.  The collection features profile pictures of cartoon apes that are procedurally generated 
#by an algorithm.  […]  As of 2022, [Bored Ape Yacht Club’s parent company,] Yuga Labs, is valued at US$4 billion. 
# This is due in large part to the sales of the Bored Ape Yacht Club NFT collection totaling over US$1 billion.  
#Various celebrities have purchased these non-fungible tokens, including Justin Bieber, Snoop Dogg, Gwyneth Paltrow and others.”

#In this project, we will go to https://opensea.io/collection/boredapeyachtclub Links to an external site. and
# select all apes with “Solid gold” fur and sort them “Price high to low” . We will Use the URL for the subsequent coding.

#Using python, we will write code that uses Selenium to access the URL from (1), click on each of the top-8 
#most expensive Bored Apes, and store the resulting details page to disk, “bayc_[N].htm” (replace [N] with the 
#ape number).

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests
from pymongo import MongoClient
import os
from bs4 import BeautifulSoup
import json
import re



os.chdir('/Applications/') #*********please mention the working directory where your chrome driver is before running
working_direc = os.getcwd()

def fun2(working_direc):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")
    
    
    #navigate to the bored ape yacht club with the specified filters
    driverpath = os.path.join(working_direc,'chromedriver')
    driver = webdriver.Chrome(executable_path=driverpath, options=options) #relative path
    driver.get('https://opensea.io/collection/boredapeyachtclub?search[sortAscending]=false&search[stringTraits][0][name]=Fur&search[stringTraits][0][values][0]=Solid%20Gold')
    time.sleep(5)

    
    #loop to click on first 8 search result and download the contents as html on local
    for i in range(1, 9):
            #product click
        products = driver.find_elements(By.CLASS_NAME, "sc-29427738-0.sc-e7851b23-1.dVNeWL.hfa-DJE.Asset--loaded") #inspect to find common element
        product = products[i-1] # Select the i-th element (0-indexed list)
        driver.execute_script("arguments[0].scrollIntoView(true);", product) #found this code on stack to avoid scroll intercept error for selenium
        product.click() #click on ith monkey
        time.sleep(5) 
                    
        html = driver.page_source
        with open(f"bayc_{i}.htm", "w") as f:
            f.write(html)
                
        driver.back() #back to main page
        time.sleep(5)
    
    time.sleep(2)
fun2(working_direc)

#################MongoDB#################
#We will Write code that goes through all 8 htm files downloaded in (2) and stores each ape’s name 
#(its number) and all its attributes in a document inside a MongoDB collection called “bayc”.


def fun3():
    
    client = MongoClient('mongodb://localhost:27017/') #connecting to mongodb server
    db = client['bayc'] #creating a database
    collection = db['bayc'] #collection inside database 
    
    for i in range(1, 9):
        filename = f'bayc_{i}.htm' #loop through each 8 files
        with open(filename, 'r') as f:
                    # Parse HTML with BeautifulSoup
                    soup = BeautifulSoup(f, 'html.parser')
        
                    # Find all attribute elements and extract name and value
                    name = soup.find('h1', {'class': 'sc-29427738-0 hKCSVX item--title'}).text #name of each monkey
                    attributes = {}
                    for elem in soup.find_all('div', {'class': 'Panel--isContentPadded item--properties'}): #nested loop to loop through all elements with the class Panel--isContentPadded item--properties
                        for attr_elem in elem.find_all('div', {'class': 'Property--type'}): #attribute type
                            attr = attr_elem.text.strip()
                            value = attr_elem.find_next_sibling('div', {'class': 'Property--value'}).text.strip() #attribute information
                            attributes[attr] = value
                            
                
                    # Store each ape's search resutl number, name and all attributes in a MongoDB collection
                    doc = {'i': i, 'name': name, 'attributes': attributes}
                    collection.insert_one(doc)
fun3()                   
 
