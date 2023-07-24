from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor,as_completed
from threading import Lock

import pandas as pd
import requests
import time

# NOTE : Due to this script involves in sending lot of request to the website, had to threads to reduce it's run time. 
# And because of this the data order that showing in the csv is different from the website's original order

#TODO : Implement a way to get page count automatically

FILE_NAME  =  "90.1266"

BASE_URL = "https://www.scmn.me"
URL  =  f"{BASE_URL}/me/ucesnici-na-trzistu/emitenti"
page_count=3

columns  =  ["company","URL" ,"PIB","Full name","Address",]
df  =  pd.DataFrame(columns  =  columns)

keyword_list = [
    "PIB",
    "Puni naziv",
    "Adresa",
]

thread_count = 20



thread_pool = ThreadPoolExecutor(max_workers = thread_count)
lock = Lock()
thread_list = []

session  =  requests.Session()
session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q = 0.9,image/avif,image/webp,*/*;q = 0.8",}
    )


def main():
    for page_number in range(1,page_count+1):
        
        response  =  get_response(URL,params={"page":page_number})

        if response.status_code == 200:
            html  =  response.text
            add_data_to_df(html)
        else:
            print(f"Error code {response.status_code}")

    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8-sig')



def add_data_to_df(html):
    
    soup  =  BeautifulSoup(html,"lxml")
    blog_post_div_list  =  soup.find_all("div",class_ = "ba-blog-post-content")

    for blog_post_div in blog_post_div_list:
        thread_list.append(thread_pool.submit(start_thread,blog_post_div))
    
    for thread in as_completed(thread_list):
        thread.result()


def start_thread(blog_post_div):
    
    row_data = []

    a_tag = blog_post_div.find("h3",class_ = "ba-blog-post-title").a
    company_name = a_tag.text.strip()
    url = f'{BASE_URL}{a_tag["href"]}'
    summary_information_data_list = get_summary_infomation_data_list(url)
    
    row_data.append(company_name)
    row_data.append(url)
    row_data += summary_information_data_list
    
    lock.acquire()    
    df.loc[len(df)+1]  =  row_data
    lock.release()


def get_summary_infomation_data_list(url):
    html = get_response(url).text
    summary_soup = BeautifulSoup(html,"lxml")
    content_div = summary_soup.find("div",class_ = "accordion-group")

    summary_information_list = []

    for keyword in keyword_list:
        value = get_value_using_keyword(keyword,content_div)
        summary_information_list.append(value)

    return summary_information_list

def get_value_using_keyword(keyword,content_div):
    for p in content_div.find_all("p"):
        if keyword in p.text:
            return get_cleaned_data_without_keyword(p,keyword)

def get_cleaned_data_without_keyword(tag,keyword):
    text = tag.text.strip()
    text = text.split(keyword)[-1]
    if text.startswith(" -"):
        text=text[3:]
    if text.startswith("-"):
        text=text[1:]
    return text



def get_response(url,*args,**kwargs):
    try:
        response  =  session.get(url,*args,**kwargs)
        return response
    except Exception as e:
        print(f"Error {e}\n Retrying in 5s")
        time.sleep(2)
        return get_response(url,*args,**kwargs)


if __name__ =="__main__":
    main()


