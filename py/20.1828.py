from bs4 import BeautifulSoup

import pandas as pd
import requests
import time


FILE_NAME = "20.1828"

columns = ["Name of the office","Name of the representative" ,"Contact"]

df = pd.DataFrame(columns = columns)

BASE_URL="http://naftalan-ih.gov.az/az/numayendelikler.html"


session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",}
    )



def main():

    response = get_response(BASE_URL)
    if response.status_code == 200:
        html = response.content.decode("utf-8")
        add_data_to_df(html)
    else:
        print(f"Error code {response.status_code}")

    
    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8')


    
def add_data_to_df(html):
    
    soup = BeautifulSoup(html,"lxml")
    tr_list=soup.find_all("tr")[1:]
    for tr in tr_list:
        row_data=get_row_data_list(tr)
        df.loc[len(df)+1] = row_data


        
def get_row_data_list(tr:BeautifulSoup):
    row_value_list=[]
    td_list=tr.find_all("td")
    
    address=td_list[1].text.strip()
    name=td_list[2].text.strip()
    contact=td_list[3].text.strip()

    row_value_list.append(address)
    row_value_list.append(name)
    row_value_list.append(contact)

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


