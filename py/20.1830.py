from bs4 import BeautifulSoup

import pandas as pd
import requests
import time


FILE_NAME = "20.1830"

columns = ["Name","role","Description"]

df = pd.DataFrame(columns = columns)

BASE_URL="http://agstafa-ih.gov.az/az/icra-hakimiyyetinin-bascisi.html"


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
    div_list=soup.find_all(class_="info_content")[1:]
    for div in div_list:
        row_data=get_row_data_list(div)
        df.loc[len(df)+1] = row_data


        
def get_row_data_list(div:BeautifulSoup):
    row_value_list=[]
    p_tag=div.find("p",align="center")
    role=p_tag.strong.text.strip()
    p_tag.strong.decompose()
    name=p_tag.text.strip()
    description=get_description_from_div(div)

    row_value_list.append(name)
    row_value_list.append(role)
    row_value_list.append(description)

    return row_value_list

def get_description_from_div(div:BeautifulSoup):
    description=""
    description_tag_list=div.find_all("p",class_=False)
    for p_tag in description_tag_list:
        description+=p_tag.text.strip()
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


