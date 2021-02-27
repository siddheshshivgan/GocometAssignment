import tkinter as tk
from tkinter import ttk

from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
import json
import pandas as pd
import requests
import time
from selectorlib import Extractor
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def search_amazon():
    prodName = ProductEntry.get()
    numProd = int(NumEntry.get())
    sortBy = SortEntry.get()
    maxR = maxEntry.get()
    minR = minEntry.get()
    pin = PincodeEntry.get()
    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')
    driver = webdriver.Chrome(ChromeDriverManager().install())

    # Amazon Scraping
    driver.get('https://www.amazon.in')
    search_address = driver.find_element_by_id('glow-ingress-line2').click()
    driver.implicitly_wait(1)
    enterPin = driver.find_element_by_id('GLUXZipUpdateInput').send_keys(pin)
    time.sleep(1)
    submitPin = driver.find_element_by_id('GLUXZipUpdate').click()
    time.sleep(2)
    search_box = driver.find_element_by_id('twotabsearchtextbox').send_keys(prodName)
    driver.implicitly_wait(3)
    search_button = driver.find_element_by_id("nav-search-submit-text").click()
    time.sleep(5)

    # SORT
    if sortBy != 'Featured':
        sort_drop = driver.find_element_by_class_name('a-dropdown-label').click()
        time.sleep(2)
        if sortBy == 'Price: Low to High':
            sort = driver.find_element_by_xpath(
                ("//li[@class='a-dropdown-item']/a[@id='s-result-sort-select_1']")).click()
            time.sleep(3)
        elif sortBy == 'Price: High to Low':
            sort = driver.find_element_by_xpath(
                ("//li[@class='a-dropdown-item']/a[@id='s-result-sort-select_2']")).click()
            time.sleep(3)
        elif sortBy == 'Newest Arrivals':
            sort = driver.find_element_by_xpath(
                ("//li[@class='a-dropdown-item']/a[@id='s-result-sort-select_4']")).click()
            time.sleep(3)
    else:
        pass

    # MAX-MIN
    if maxR != '0' and minR != '0':
        set_min = driver.find_element_by_id('low-price').send_keys(minR)
        set_max = driver.find_element_by_id('high-price').send_keys(maxR)
        driver.find_element_by_id('high-price').send_keys(Keys.ENTER)
        time.sleep(3)

    url_list = []
    for i in range(int(3)):
        page_ = i + 1
        url_list.append(driver.current_url)
        click_next = driver.find_element_by_class_name('a-last').click()
        time.sleep(3)
        print("Page " + str(page_) + " grabbed")
    with open('search_results_urls.txt', 'w') as filehandle:
        for result_page in url_list:
            filehandle.write('%s\n' % result_page)
            print("---DONE---")

    with open("search_results_urls.txt", 'r') as urllist:
        alldetails = []
        for url in urllist.read().splitlines():
            data = scrape(url)
            if data:
                for product in data['products']:
                    temp = {
                        'Product Name': product['title'],
                        'Price': product['price'],
                        'Rating': product['rating'],
                        'Source': 'Amazon',
                        'URL': 'https://www.amazon.in/'+product['url']
                    }
                    print("Saving Product: %s" % product['title'].encode('utf8'))
                    alldetails.append(temp)
        pd.DataFrame(alldetails)
        aoutput = pd.DataFrame(alldetails)
        aoutput = aoutput.head(numProd // 2)
        aoutput.to_csv('aoutput.csv', index=False)

    # Flipkart Scraping
    products, prices, ratings, url= [], [], [], []
    driver.get('https://www.flipkart.com/')
    close = driver.find_element_by_xpath('/html/body/div[2]/div/div/button').click()
    time.sleep(1)
    fsearch_box = driver.find_element_by_class_name('_3704LK').send_keys(prodName)
    time.sleep(1)
    fsearch_button = driver.find_element_by_xpath(
        '//*[@id="container"]/div/div[1]/div[1]/div[2]/div[2]/form/div/button').click()
    time.sleep(3)
    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")

    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        url.append(elem.get_attribute("href"))
    url1 = url[14:38]

    for a in soup.findAll('a', href=True, attrs={'class': '_1fQZEK'}):
        name = a.find('div', attrs={'class': '_4rR01T'})
        price = a.find('div', attrs={'class': '_30jeq3 _1_WHN1'})
        rating = a.find('div', attrs={'class': '_3LWZlK'})
        products.append(name.text)
        prices.append(price.text)
        ratings.append(rating.text)

    # Storing scraped content
    foutput = pd.DataFrame({'Product Name': products, 'Price': prices, 'Rating': ratings, 'Source': 'Flipkart', 'URL': url1})
    foutput = foutput.head(numProd // 2 + 1)
    foutput.to_csv('foutput.csv', index=False, encoding='utf-8')
    driver.quit()
    data1 = pd.read_csv('aoutput.csv')
    data2 = pd.read_csv('foutput.csv')
    final_op = pd.concat([data1, data2], axis=0)
    final_op.to_excel('final_op.xlsx', index=False)
    exit(0)


def scrape(url):
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'siddheshshivgan2306@gmail.com'
    }

    # Download the page using requests
    print("Downloading %s" % url)
    r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n" % url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d" % (url, r.status_code))
        return None
    # Pass the HTML of the page and create
    return e.extract(r.text)


if __name__ == '__main__':
    e = Extractor.from_yaml_file('search_results.yml')
    root = tk.Tk()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    xLeft = int((w / 2) - (1050 / 2))
    yTop = int((h / 2) - (300 / 2))
    strg = "1050x300+" + str(xLeft) + "+" + str(yTop)
    root.geometry(strg)
    root.title("Web Crawler")
    root.resizable(0, 0)
    root.wm_iconbitmap('search.ico')

    Labelfont = ("Times New Roman", 12)
    titleLabel = tk.Label(root, text="Product Search", font=("Segoe UI", 15)).place(x=480, y=10)
    ProductNameLabel = tk.Label(root, text="Product Name :", font=Labelfont).place(x=390, y=55)
    ProductEntry = tk.Entry(root, width=30)
    ProductEntry.place(x=530, y=60)

    NumOfProdLabel = tk.Label(root, text="Number of Products :", font=Labelfont).place(x=390, y=85)
    intg = tk.IntVar()
    NumTup = [i for i in range(10, 51)]
    NumEntry = ttk.Combobox(root, state="readonly", width=27, textvariable=intg)
    NumEntry['values'] = tuple(NumTup)
    NumEntry.current(0)
    NumEntry.place(x=530, y=90)

    SortByLabel = tk.Label(root, text="Sort By :", font=Labelfont).place(x=390, y=115)
    n = tk.StringVar()
    SortEntry = ttk.Combobox(root, state="readonly", width=27, textvariable=n)
    SortEntry['values'] = ('Price: Low to High', 'Price: High to Low', 'Featured', 'Newest Arrivals')
    SortEntry.current(2)
    SortEntry.place(x=530, y=120)

    PriceLabel = tk.Label(root, text="Price Range :", font=Labelfont).place(x=390, y=145)
    m = tk.StringVar()
    PriceEntry = ttk.Combobox(root, state="readonly", width=27, textvariable=m)
    PriceEntry['values'] = ('No limit', 'In particular Range')
    PriceEntry.current(0)
    PriceEntry.place(x=530, y=145)

    PincodeLabel = tk.Label(root, text="Delivery Pincode :", font=Labelfont).place(x=390, y=205)
    PincodeEntry = tk.Entry(root, width=30)
    PincodeEntry.insert(0, '400072')
    PincodeEntry.place(x=530, y=210)
    minlabel = tk.Label(root, text="Min:", font=Labelfont).place(x=530, y=175)
    minEntry = tk.Entry(root, width=8)
    minEntry.place(x=565, y=180)
    maxlabel = tk.Label(root, text="Max:", font=Labelfont).place(x=620, y=175)
    maxEntry = tk.Entry(root, width=8)
    maxEntry.place(x=655, y=180)
    minEntry.insert(0, 0)
    maxEntry.insert(0, 0)
    SearchButton = tk.Button(root, text="Search", font=Labelfont, width=10, command=search_amazon).place(x=500, y=250)
    root.mainloop()
