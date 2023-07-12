from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

FILE_NAME = "90.0126"



columns = ["Component","Component URL","ISIN","Trading Location","Issuer Country"]

df = pd.DataFrame(columns = columns)


BASE_URL="https://live.euronext.com"
AJAX_URL = "https://live.euronext.com/en/ajax/getIndexCompositionFull/PTING0200002-XLIS"


session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    })


def main():
    response = get_response(AJAX_URL)
    if response.status_code == 200:
        html = response.text
        add_data_to_df(html)
    else:
        print(f"Error code {response.status_code}")
    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8')


    
def add_data_to_df(html):
    
    soup = BeautifulSoup(html,"lxml")
    tbody = soup.find("tbody")
    for tr in tbody.find_all("tr"):
        row_data_list=get_row_data_list(tr)
        df.loc[len(df)+1] = row_data_list
                

def get_row_data_list(tr):
    row_data_list=[]
    for td in tr.find_all("td"):
        if td.find("a"):
            row_data_list.append(td.text.strip())
            row_data_list.append(BASE_URL+td.a["href"].strip())
        else:
            row_data_list.append(td.text.strip())

    return row_data_list



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


