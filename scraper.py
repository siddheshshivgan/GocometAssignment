import tkinter as tk
from tkinter import ttk

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
    numProd = NumEntry.get()
    sortBy = SortEntry.get()
    maxR = int(maxEntry.get())
    minR = int(minEntry.get())
    pin = PincodeEntry.get()
    time.sleep(10)

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get('https://www.amazon.in')
    search_address = driver.find_element_by_id('glow-ingress-line2').click()
    driver.implicitly_wait(2)
    enterPin = driver.find_elements_by_id('GLUXZipUpdateInput').send_keys(pin)
    submitPin = driver.find_element_by_id('GLUXZipUpdate-announce').click()
    driver.implicitly_wait(3)
    search_box = driver.find_element_by_id('twotabsearchtextbox').send_keys(prodName)
    search_button = driver.find_element_by_id("nav-search-submit-text").click()
    driver.implicitly_wait(5)
    try:
        num_page = driver.find_element_by_xpath('//*[@class="a-pagination"]/li[6]')
    except NoSuchElementException:
        num_page = driver.find_element_by_class_name('a-last').click()
    driver.implicitly_wait(5)

    url_list = []
    url_list.append(driver.current_url)
    driver.implicitly_wait(5)
    click_next = driver.find_element_by_class_name('a-last').click()
    url_list.append(driver.current_url)
    driver.quit()
    with open('search_results_urls.txt', 'w') as filehandle:
        for result_page in url_list:
            filehandle.write('%s\n' % result_page)
            print("---DONE---")


def scrape(url):
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.in/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
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
    root = tk.Tk()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    xLeft = int((w / 2) - (350 / 2))
    yTop = int((h / 2) - (280 / 2))
    strg = "350x300+" + str(xLeft) + "+" + str(yTop)
    root.geometry(strg)
    root.title("Product Search")
    root.resizable(0, 0)
    root.wm_iconbitmap('search.ico')

    Labelfont = ("Times New Roman", 12)
    titleLabel = tk.Label(root, text="Product Search", font=("Segoe UI", 20)).place(x=80, y=10)
    ProductNameLabel = tk.Label(root, text="Product Name :", font=Labelfont).place(x=10, y=55)
    ProductEntry = tk.Entry(root, width=30)
    ProductEntry.place(x=150, y=60)

    NumOfProdLabel = tk.Label(root, text="Number of Products :", font=Labelfont).place(x=10, y=85)
    intg = tk.IntVar()
    NumTup = [i for i in range(10, 51)]
    NumEntry = ttk.Combobox(root, state="readonly", width=27, textvariable=intg)
    NumEntry['values'] = tuple([10])
    NumEntry.current(0)
    NumEntry.place(x=150, y=90)

    SortByLabel = tk.Label(root, text="Sort By :", font=Labelfont).place(x=10, y=115)
    n = tk.StringVar()
    SortEntry = ttk.Combobox(root, state="readonly", width=27, textvariable=n)
    SortEntry['values'] = ('Price: Low to High', 'Price: High to Low', 'Featured', 'Newest Arrivals')
    SortEntry.current(2)
    SortEntry.place(x=150, y=120)

    PriceLabel = tk.Label(root, text="Price Range :", font=Labelfont).place(x=10, y=145)
    m = tk.StringVar()
    PriceEntry = ttk.Combobox(root, state="readonly", width=27, textvariable=m)
    PriceEntry['values'] = ('No limit', 'In particular Range')
    PriceEntry.current(0)
    PriceEntry.place(x=150, y=145)

    PincodeLabel = tk.Label(root, text="Delivery Pincode :", font=Labelfont).place(x=10, y=205)
    PincodeEntry = tk.Entry(root, width=30)
    PincodeEntry.insert(0, '400072')
    PincodeEntry.place(x=150, y=210)
    minlabel = tk.Label(root, text="Min:", font=Labelfont).place(x=150, y=175)
    minEntry = tk.Entry(root, width=8)
    minEntry.place(x=185, y=180)
    maxlabel = tk.Label(root, text="Max:", font=Labelfont).place(x=242, y=175)
    maxEntry = tk.Entry(root, width=8)
    maxEntry.place(x=280, y=180)
    minEntry.insert(0, 0)
    maxEntry.insert(0, 0)
    SearchButton = tk.Button(root, text="Search", font=Labelfont, width=10, command=search_amazon()).place(x=125, y=250)
    root.mainloop()
    e = Extractor.from_yaml_file('search_results.yml')
    # product_data = []
    with open("search_results_urls.txt", 'r') as urllist:
        alldetails = []
        for url in urllist.read().splitlines():
            data = scrape(url)
            if data:
                for product in data['products']:
                    product['search_url'] = url
                    print("Saving Product: %s" % product['title'].encode('utf8'))
                    alldetails.append(product)
            pd.DataFrame(alldetails)
            data = pd.DataFrame(alldetails)
            data.to_excel('Amazon_tv.xlsx')
