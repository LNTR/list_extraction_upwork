from bs4 import BeautifulSoup

import pandas as pd
import requests
import time


FILE_NAME = "20.1835"

columns = ["Name with position" ,"Description"]

df = pd.DataFrame(columns = columns)

BASE_URL="http://gedebey-ih.gov.az/az/ih-bascisinin-muavinleri.html"


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
    div_tag=soup.find("div",class_="metn")
    div_tag.h1.decompose()
    name=div_tag.find("p").text.strip()
    description=""
    for p in div_tag.find_all("p")[1:]:

        if p.find("strong"):
            df.loc[len(df)+1] = [name,description]
            name=p.text.strip()
            description=""

        else:
            description+="\n"+p.text.strip()
            
    df.loc[len(df)+1] = [name,description]


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


