from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

import pandas as pd
import requests
import time
import re


FILE_NAME = "90.1267"

columns = ["Company Name" ,"PIB","Website URL","Basic Infomation"]
    
pattern_list = [
    re.compile(r"PIB",re.IGNORECASE),
    re.compile(r"web",re.IGNORECASE)
]

df = pd.DataFrame(columns = columns)

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

BASE_URL = "https://www.scmn.me"
URL  =  f"{BASE_URL}/en/ucesnici-na-trzistu/investicioni-fondovi/drustva-za-upravljanje-investicionim-fondom"

session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",}
    )


def main():
    response = get_response(URL)
    if response.status_code == 200:
        html = response.text
        add_data_to_df(html)
    else:
        print(f"Error code {response.status_code}")

    
    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8-sig')


    
def add_data_to_df(html):
    
    soup = BeautifulSoup(html,"lxml")
    accordion_group_div_list = soup.find_all("div",class_="accordion-group")

    for accordian_div in accordion_group_div_list:
        row_data=get_row_data_list(accordian_div)
        df.loc[len(df)+1] = row_data
        
def get_row_data_list(accorian_div):
    row_value_list=[]
    context_div=accorian_div.find(class_="content-text")
    
    company_name=context_div.p.text.strip()
    context_div.p.decompose()

    factory_details_list=get_matched_text_for_keywords(context_div)

    row_value_list.append(company_name)
    row_value_list+=factory_details_list

    return row_value_list

        
def get_matched_text_for_keywords(page_text_div:BeautifulSoup):
    
    matched_text_list=[]
    for pattern in pattern_list:
        matched_element=page_text_div.find("p",string=pattern)
        if matched_element:
            cleaned_text=get_cleaned_data(matched_element)
            matched_text_list.append(cleaned_text)
            matched_element.decompose()
        else:
            matched_text_list.append("")

    matched_text_list.append(page_text_div.text.strip())
    return matched_text_list
    

def get_cleaned_data(p_tag):
    text=p_tag.text.strip()
    text=text.split(":")[-1]
    if text.startswith("//"):
        text=text[2:]
    return text


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


