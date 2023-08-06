from bs4 import BeautifulSoup

import pandas as pd
import requests
import time


FILE_NAME = "60.0103"

columns = ["Debtor","Application number","registration number","tax number","Date of birth","Procedure type","URL"]
df = pd.DataFrame(columns = columns)

BASE_URL="https://www.ajpes.si/eInsolv"
URL=f"{BASE_URL}/rezultati.asp"

payload={
        "podrobno":0,
        "stStevilka":"",	
        "dolznik":"_", # Instead of passing every single letter, the passed underscore will match any character
        "naslovDolznika":"",
        "maticnaStevilka":"",	
        "davcnaStevilka":"",
        "rojstniDatum":"",
        "emso":"",
        }

session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",}
    )

def main():
    
    response = get_response(URL,params=payload,timeout=None)
    if response.status_code == 200:
        html = response.content.decode('utf-8')
        add_data_to_df(html)
    else:
        print(f"Error code {response.status_code}")

    
    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8')


     
def add_data_to_df(html):
    
    soup = BeautifulSoup(html,"lxml")
    tbody=soup.find("table",id="tableRezultati").tbody
    for tr in tbody.find_all("tr"):
        row_data=get_row_data_list(tr)
        df.loc[len(df)+1] = row_data


        
def get_row_data_list(tr:BeautifulSoup):
    row_value_list=[]
    
    td_list=tr.find_all("td")

    debetor=td_list[0].text.strip()
    url=f'{BASE_URL}/{td_list[0].a["href"]}'
    application_number=td_list[1].text.strip()
    register_number=td_list[2].text.strip()
    tax_number=td_list[3].text.strip()
    dob=td_list[4].text.strip()
    producer_type=td_list[5].text.strip()

    row_value_list.append(debetor)
    row_value_list.append(application_number)
    row_value_list.append(register_number)
    row_value_list.append(tax_number)
    row_value_list.append(dob)
    row_value_list.append(producer_type)
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
    

if __name__ == "__main__":
    main()

