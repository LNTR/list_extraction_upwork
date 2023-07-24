from bs4 import BeautifulSoup

import pandas as pd
import requests
import time
import re
import ftfy



FILE_NAME = "90.1280"

df_columns = ["Company Name","Address","Tel No","Email",]
    
div_match_pattern=re.compile(r"wb_LayoutGrid")
empty_row_placeholder_word="E  UL."

df = pd.DataFrame(columns = df_columns)

BASE_URL="https://www.advokatskakomora.me"
URL  =  f"{BASE_URL}/mojkovac.html"

session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",}
    )


def main():
    page_url_list=get_url_list_of_all_paginations()
    if page_url_list==[]:
        page_url_list.append(URL)
    for url in page_url_list:
        scrape_data_from_url_and_add_to_df(url)

    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8-sig')

def scrape_data_from_url_and_add_to_df(url):
    response = get_response(url)
    if response.status_code == 200:
        html = response.text
        add_data_to_df(html)
    else:
        print(f"Error code {response.status_code}")


def get_url_list_of_all_paginations():
    url_list=[]
    response = get_response(URL)
    html = response.text
    soup=BeautifulSoup(html,"lxml")
    ul_tag=soup.find(id="Pagination1")
    if ul_tag:
        for li_tag in ul_tag.find_all("li"):
            url=f"{BASE_URL}/{li_tag.a['href'][1:]}"
            url_list.append(url)
    
    return url_list


def add_data_to_df(html):
    
    div_list=get_div_list_without_headers_and_footers_and_empty_rows(html)
    for div in div_list:
        add_row_to_df(div)


def add_row_to_df(div):
    try:
        row_data=get_row_data_list(div)
        df.loc[len(df)+1] = get_row_data_list_without_garbage_unicode(row_data)
    except Exception as e:
        print(e)
        print("Note... The above error was generated due to the relevent row being empty. You don't have to worry about it\n")
        # P.S : Don't worry about this messege


def get_div_list_without_headers_and_footers_and_empty_rows(html):

    soup = BeautifulSoup(html,"lxml")
    remove_header_and_footer_divs(soup)
    div_list=get_div_list_without_empty_rows(soup)

    return div_list

def remove_header_and_footer_divs(soup):
    div_list = soup.find_all("div",id=div_match_pattern)
    for div in div_list[:4]+div_list[-4:]:
        div.decompose()

def get_div_list_without_empty_rows(soup):
    div_list_with_empty_rows = soup.find_all("div",id=div_match_pattern)
    div_list=[]

    for div in div_list_with_empty_rows:
        if not(empty_row_placeholder_word in div.text.strip()):
            div_list.append(div)
    return div_list

def get_row_data_list(div):
    row_value_list=[]
    row_div=div.find(class_="row")
    column_1_data=get_column_1_data(row_div)
    column_2_data=get_column_2_data(row_div)

    row_value_list+=column_1_data
    row_value_list+=column_2_data

    return row_value_list

def get_column_1_data(row_div):
    row=[]
    column_1_data=row_div.find("div",class_="col-1").div.span

    company_name=column_1_data.strong.text.strip()
    column_1_data.strong.decompose()
    address=column_1_data.text.strip()

    row.append(company_name)
    row.append(address)

    return row



def get_column_2_data(row_div):
    row=[]
    column_2_data=row_div.find("div",class_="col-2").div.span
    telephone=get_cleaned_data(column_2_data.strong)
    column_2_data.strong.decompose()
    if column_2_data.a:
        email=column_2_data.a.text.strip()
    else:
        email=""
    row.append(telephone)
    row.append(email)

    return row


def get_cleaned_data(strong_tag):
    text=strong_tag.text.strip().lower()
    text=text.replace("mob","tel")
    text=text.split("tel.")[-1]
    text=text.replace("/fax.","")
    text=text.replace("tel","")
    text=text.replace("email","")


    return text

def get_row_data_list_without_garbage_unicode(row_data_list):
    row_data_list_without_trash=[]
    
    for row_data in row_data_list:
        fixed_data=ftfy.fix_text(row_data)
        fixed_data=fixed_data.replace("Å","S")
        fixed_data=fixed_data.replace("Ä","Đ")

        row_data_list_without_trash.append(fixed_data)
    return row_data_list_without_trash

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


