from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

import pandas as pd
import requests
import time
import re

 
 

FILE_NAME = "90.1263"



columns = ["Factoring company","URL" ,"head office","Licence No","Executive director","Board of Directors"]
pattern_list=[
    re.compile(r"Head office",re.IGNORECASE),
    re.compile(r"Licence No",re.IGNORECASE),
    re.compile(r"Executive director",re.IGNORECASE),
]

df = pd.DataFrame(columns = columns)

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


BASE_URL="https://cbcg.me"
URL = f"{BASE_URL}/en/core-functions/supervision/financial-service-providers/companies-for-purchase-of-receivables"

session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",}
    )


def main():
    response = get_response(URL,verify=False)
    if response.status_code == 200:
        html = response.text
        add_data_to_df(html)
    else:
        print(f"Error code {response.status_code}")

    
    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8-sig')


    
def add_data_to_df(html):
    
    soup = BeautifulSoup(html,"lxml")
    children_listing_div = soup.find("div",class_="children-listing")
    for child_div in children_listing_div.find_all("div",recursive=False):
        row_data=get_row_data_list(child_div)
        df.loc[len(df)+1] = row_data
        
def get_row_data_list(child_div):
    row_value_list=[]
    a_tag=child_div.find("a")
    if a_tag:
        url=f'{BASE_URL}{a_tag["href"]}'
        row_value_list.append(a_tag.text.strip())
        row_value_list.append(url)
        factory_details_list=get_factory_details(url)
        row_value_list+=factory_details_list
    return row_value_list

        

def get_factory_details(url):
    response = get_response(url,verify=False)
    factory_soup=BeautifulSoup(response.text,"lxml")
    page_text_div=factory_soup.find(class_="page-text")
    matched_text_list=get_matched_text_for_patterns(page_text_div)
    board_of_directors=get_board_of_directors(page_text_div)
    return matched_text_list+[board_of_directors]

def get_matched_text_for_patterns(page_text_div:BeautifulSoup):
    
    matched_text_list=[]
    for pattern in pattern_list:
        strong_tag=page_text_div.find("strong",string=pattern)
        if strong_tag:
            cleaned_data=get_cleaned_data(strong_tag.parent)
            matched_text_list.append(cleaned_data)
        
    return matched_text_list
    

def get_cleaned_data(p_tag):
    text=p_tag.text.strip()
    text=text.split(":")[-1]
    text=text.split(".")[-1]
    
    return text


def get_board_of_directors(page_text_div:BeautifulSoup):
    directors=[]
    ol_div=page_text_div.find("ol")
    for li in ol_div.find_all("li"):
        directors.append(li.text.strip())
    
    return '\n'.join(directors)

def get_response(url,*args,**kwargs):
    try:
        response = session.get(url,*args,**kwargs)
        return response
    except Exception as e:
        print(f"Error {e}\n Retrying in 5s")
        time.sleep(2)
        return get_response(url,*args,**kwargs)


if __name__ == "__main__":
    main()


