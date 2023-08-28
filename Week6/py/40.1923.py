from bs4 import BeautifulSoup

import pandas as pd
import requests
import time
import re


FILE_NAME = "40.1923"

columns = ["Name","Action","Filed Date","PDF Url"]

df = pd.DataFrame(columns = columns)


BASE_URL="https://www.securities.ok.gov"
URL=f"{BASE_URL}/Enforcement/Orders/"

payload={
        'Display' : r"%",
        'SortID' : "Filed Date",
        'SearchText' : "",
        'CaseName' : "",
        'CurrentPage' :	1
         }

session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",}
    )

navigation_pattern=re.compile(r"Page \d+ of \d+")

def main():
    has_next_page=True
    response = get_response(f"{BASE_URL}/Main")
    
    while has_next_page:
        response = get_response(URL,params=payload)

        if response.status_code == 200:
            html = response.content.decode("windows-1252")
            add_data_to_df(html)
            has_next_page=is_next_page_exists(html)
        
        else:
            print(f"Error code {response.status_code}")
            has_next_page=False
        payload["CurrentPage"]+=1
    
    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8')

def is_next_page_exists(html):
    soup=BeautifulSoup(html,"lxml")
    if soup.find("form",attrs={"name":"NextPage"}):
        return True
    return False

def add_data_to_df(html):
    
    soup = BeautifulSoup(html,"lxml")
    named_div_list=soup.find_all("a",attrs={"target":"_top","title":True})
    for named_div in named_div_list:
        for tr in named_div.parent.parent.find_next_siblings("tr",recursive=False):
            if (named_div.text.strip()!="" and tr!="\n" and not navigation_pattern.search(tr.text)):
                row_data=[named_div.text.strip()]
                row_data+=get_row_data_list(tr)
                df.loc[len(df)+1] = row_data

        
def get_row_data_list(tr:BeautifulSoup):
    row_value_list=[]

    td=tr.find("font",attrs={"face":True}).parent
    pdf_url=f'{URL}{td.a["href"]}'
    action_name=td.a.text.strip()
    filed_date=td.font.text.strip().replace("Filed:\xa0","")

    row_value_list.append(action_name)
    row_value_list.append(filed_date)
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


