from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

FILE_NAME = "90.0117"



headers  =  {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}
columns = ["Name","Information"]

df = pd.DataFrame(columns = columns)

URL = "https://www.fsrc.kn/regulated-entities"

session = requests.Session()

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
    div_list = soup.find_all(class_ = "fbContent_qListItem")
    for div in div_list:
        company_name = div.div.div.h3.text.strip()

        body_data_div=div.div.find("div",class_="qListItem_introtext")
        body_data=BeautifulSoup(str(body_data_div).replace("<br/>","\n"),"lxml").text
        body_data=body_data.replace("\xa0","\n")

        df.loc[len(df)+1] = [company_name,body_data]
        

    

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


