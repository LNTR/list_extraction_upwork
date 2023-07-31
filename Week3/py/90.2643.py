from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor,as_completed

import pandas as pd
import requests
import time
 

FILE_NAME = "90.2643"



columns = ["Broker names","broker filer code" ,"addresses","phones"]

df = pd.DataFrame(columns = columns)

BASE_URL="https://www.cbp.gov"
URL = f"{BASE_URL}/about/contact/find-broker-by-port/0712"

payload={"page":None}

session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",}
    )

thread_count=20

def main():
    page_count=get_page_count(URL)
    for page_no in range(page_count):
        
        payload["page"]=page_no
        response = get_response(URL,params=payload)

        if response.status_code == 200:
            html = response.text
            add_data_to_df(html)
        else:
            print(f"Error code {response.status_code}")

    
    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8')

def get_page_count(URL):
    page_count=1
    response = get_response(URL)
    html=response.text
    homepage_soup=BeautifulSoup(html,"lxml")
    nav_tag=homepage_soup.find("nav",class_="usa-pagination")
    if nav_tag:
        last_page_div=nav_tag.find(title="Go to last page")
        if last_page_div:
            page_count=last_page_div.text
            page_count=int(page_count)
        else:
            page_count=2
    return page_count
    
def add_data_to_df(html):
    
    soup = BeautifulSoup(html,"lxml")
    table_div = soup.find("div",class_="view-content")
    table_body=table_div.find("tbody")
    add_data_list_to_df_using_threading(table_body)

def add_data_list_to_df_using_threading(table_body):
    thread_list=[]

    with ThreadPoolExecutor(max_workers=thread_count) as executor:

        for row in table_body.find_all("tr"):
            thread_list.append(executor.submit(get_row_data_list,row))
        
        for thread in as_completed(thread_list):
            row_data=thread.result()
            df.loc[len(df)+1] = row_data


        
def get_row_data_list(row:BeautifulSoup):
    row_value_list=[]
    broker_name_div=row.find("td",class_="views-field-title-1")

    broker_name=broker_name_div.text.strip()
    broker_filter_code=row.find("td",class_="views-field-field-broker-filer-code").text.strip()
    broker_url=f'{BASE_URL}{broker_name_div.a["href"]}'
    broker_contact_info_list=get_broker_contact_information(broker_url)

    row_value_list.append(broker_name)
    row_value_list.append(broker_filter_code)
    row_value_list+=broker_contact_info_list

    return row_value_list

def get_broker_contact_information(broker_url):
    broker_contact_info_list=[]

    broker_contact_info_page_response = get_response(broker_url)
    
    if broker_contact_info_page_response.status_code == 200:
        html = broker_contact_info_page_response.text
        broker_contact_info_list=get_address_and_phone_number(html)

    else:
        print(f"Error code {broker_contact_info_page_response.status_code}")

    return broker_contact_info_list
    

def get_address_and_phone_number(html):
    broker_contact_info_list=[]

    contact_info_soup=BeautifulSoup(html,"lxml")

    table_div = contact_info_soup.find("div",class_="view-content")
    
    if table_div:
        table_body=table_div.find("tbody")

        address=table_body.find("td",class_="views-field-field-location-address").text
        phone_number=table_body.find("td",class_="views-field-field-phone").text
    else:
        address=""
        phone_number=""

    broker_contact_info_list.append(address)
    broker_contact_info_list.append(phone_number)

    return  broker_contact_info_list



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


