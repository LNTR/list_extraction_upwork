from bs4 import BeautifulSoup

import pandas as pd
import requests
import time
import re


FILE_NAME = "40.1927"

columns = ["Name","Date","PDF Url","Description"]


df = pd.DataFrame(columns = columns)


BASE_URL="https://www.dobs.pa.gov"
URL=f"{BASE_URL}/For%20Media/Pages/2021-Enforcement-Orders.aspx"

id_name_pattern=re.compile(r"Main_PageContent",re.IGNORECASE)

session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",}
    )


def main():

    response = get_response(URL)
    if response.status_code == 200:
        html = response.content.decode("utf-8")
       
        add_data_to_df(html)
        
    else:
        print(f"Error code {response.status_code}")

    
    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8')


def add_data_to_df(html):
    
    soup = BeautifulSoup(html,"lxml")
    div=soup.find_all("div",id=id_name_pattern)[1]
    anchor_list=div.find_all("a",href=True)
    for anchor in anchor_list:
        row=anchor.parent.parent

        row_data=get_row_data_list(row)
        df.loc[len(df)+1] = row_data


        
def get_row_data_list(row:BeautifulSoup):
    row_value_list=[]
    
    anchor_tag=row.find("a")
    pdf_url=f'{BASE_URL}{anchor_tag["href"]}'
    name=anchor_tag.text.strip()
    date=get_date(pdf_url)
    anchor_tag.decompose()
    row.strong.decompose()
    description=get_description(row)

    row_value_list.append(name)
    row_value_list.append(date)
    row_value_list.append(pdf_url)
    row_value_list.append(description)

    return row_value_list

def get_date(pdf_url):
    file_name=pdf_url.split("/")[-1]
    month=file_name[:2]
    day=file_name[2:4]
    year=pdf_url.split("/")[-2]
    return f"{month}/{day}/{year}"

def get_description(row):
    description=row.text.strip()
    description=description.replace("(PDF)","")
    return description

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


