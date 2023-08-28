from bs4 import BeautifulSoup

import pandas as pd
import requests
import time
import re


FILE_NAME = "40.1939"

columns = ["Name","Year","PDF Url"]

df = pd.DataFrame(columns = columns)


BASE_URL="https://www.dobs.pa.gov"
URL=f"{BASE_URL}/For%20Media/Pages/2009-Enforcement-Orders.aspx"

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
    for anchor_tag in anchor_list:
        if len(anchor_tag.text.strip())>3:
            row_data=get_row_data_list(anchor_tag)
            df.loc[len(df)+1] = row_data


        
def get_row_data_list(anchor_tag:BeautifulSoup):
    row_value_list=[]
    
    pdf_url=f'{BASE_URL}{anchor_tag["href"]}'
    name=anchor_tag.text.strip()
    year=pdf_url.split("/")[-2]

    row_value_list.append(name)
    row_value_list.append(year)
    row_value_list.append(pdf_url)

    return row_value_list



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


