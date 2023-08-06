from bs4 import BeautifulSoup

import pandas as pd
import requests
import time


FILE_NAME = "40.1067"

columns = ["Date","Topic" ,"Description","URL"]

df = pd.DataFrame(columns = columns)

BASE_URL="https://www.fme.is"
URL = f"{BASE_URL}/utgefid-efni/frettir-og-tilkynningar/gagnsaeistilkynningar/page"


session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",}
    )



def main():

    next_page_available=True
    current_page_number=0

    while next_page_available:

        current_page_number+=1
        current_url=f"{URL}/{current_page_number}"
        response = get_response(current_url)
        if response.status_code == 200:
            html = response.content.decode("utf-8")
            add_data_to_df(html)
        else:
            print(f"Error code {response.status_code}")

        next_page_available=has_a_next_page(html)
    
    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8')


    
def add_data_to_df(html):
    
    soup = BeautifulSoup(html,"lxml")
    for div_tag in soup.find_all(class_="item"):
        row_data=get_row_data_list(div_tag)
        df.loc[len(df)+1] = row_data


        
def get_row_data_list(div_tag:BeautifulSoup):
    row_value_list=[]
    date=div_tag.find("span",class_="date").text.strip()
    topic=div_tag.find("a").text
    more_tag=div_tag.find(class_="more")
    if more_tag:
        more_tag.decompose()

    description=div_tag.find(class_="summary").text
    url=f'{BASE_URL}{div_tag.find("a")["href"]}'

    row_value_list.append(date)
    row_value_list.append(topic)
    row_value_list.append(description)
    row_value_list.append(url)

    return row_value_list

def get_response(url,*args,**kwargs):
    try:
        response = session.get(url,*args,**kwargs)
        return response
    except Exception as e:
        print(f"Error {e}\n Retrying in 5s")
        time.sleep(2)
        return get_response(url,*args,**kwargs)


def has_a_next_page(html):
    soup=BeautifulSoup(html,"lxml")
    if soup.find("li",class_="next").a:
        return True
    return False


if __name__ == "__main__":
    main()


