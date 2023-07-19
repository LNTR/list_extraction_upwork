from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

FILE_NAME = "90.0119"



columns = ["Company Name"]

df = pd.DataFrame(columns = columns)


URL = "https://tcifsc.tc/trust-companies-licensed-trust-companies/"

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
    li_list = soup.find("ul",attrs={"data-rte-list":"default"}).find_all("li")
    for li in li_list:
        df.loc[len(df)+1] = [li.text.replace("\xa0","\n")]
        

        


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


