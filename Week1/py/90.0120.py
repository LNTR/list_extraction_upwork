from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

FILE_NAME = "90.0120"



columns = ["Company Name","CLASS OF LICENCE","ADDRESS","WEBSITE ADDRESS"]

df = pd.DataFrame(columns = columns)


URL = "https://tcifsc.tc/company-managers-company-managers-agents/"

session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    })


def main():
    response = get_response(URL)
    if response.status_code == 200:
        html = response.text
        add_data_to_df(html)
    else:
        print(f"Error code {response.status_code}")

    
    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8')


    
def add_data_to_df(html):
    
    soup = BeautifulSoup(html,"lxml")
    tr_list = soup.find_all("tr",class_="wptb-row")
    for tr in tr_list[1:]:
        row_data=get_row_data_list(tr)
        df.loc[len(df)+1] = row_data
        
def get_row_data_list(tr):
    match_value_list=[]
    for td in tr.find_all("td"):
        a_tag=td.find("a")
        if a_tag:
            match_value_list.append(a_tag["href"])
            
        else:
            match_value_list.append(td.text.replace("\xa0","").replace("’","'").strip())
    return match_value_list

        


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


