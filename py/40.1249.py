from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from io import BytesIO
from concurrent.futures import ProcessPoolExecutor,as_completed

import pandas as pd
import requests
import time
import re


FILE_NAME = "40.1249"

columns = ["PDF URL","Title","Entity Name","Data"]
df = pd.DataFrame(columns = columns)

BASE_URL="https://www.bsi.si"
URL = f"{BASE_URL}/en/financial-stability/banking-system-supervision/supervisory-disclosure/publication-of-administrative-penalties"


head_pattern=re.compile(r"legal +person",re.IGNORECASE)
foot_pattern=re.compile(r"Information (regarding|on) breach")

process_count=5

session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",}
    )



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
    table_div= soup.find("table")
    tr_list=table_div.find_all("tr")[1:]
    add_data_to_df_using_concurrency(tr_list)
    

def add_data_to_df_using_concurrency(tr_list:list):
    process_list=[]
    with ProcessPoolExecutor(max_workers=process_count) as executor:
        for tr in tr_list:
            # !IMPORTANT NOTE :  BeautifulSoup isn't compatible with multiprocessing.
            # (It gave an error when tr is past as a BeautifulSoup object). So passing the string version of 
            # element and resouping it using BeautifulSoup constructor was the only option I had.
            tr_string=str(tr) 
            process_list.append(executor.submit(get_row_data_list,tr_string))
        
        for process in as_completed(process_list):
            row_data=process.result()
            df.loc[len(df)+1] = row_data


def get_row_data_list(tr_string):
    tr=BeautifulSoup(tr_string,"lxml")
    row_value_list=[]
    anchor_tag=tr.find("a")
    pdf_url=get_url_from_a_tag(anchor_tag)
    title=tr.td.text.strip()
    pdf_details_list=get_entity_name_and_pdf_content(pdf_url)

    row_value_list.append(title)
    row_value_list.append(pdf_url)
    row_value_list+=pdf_details_list

    return row_value_list
    

def get_url_from_a_tag(a_tag:BeautifulSoup):
    url=a_tag["href"]
    if url.startswith("http"):
        return url
    return f"{BASE_URL}{url}"

def get_entity_name_and_pdf_content(pdf_url):
    response=session.get(pdf_url)
    pdf_content=response.content

    stream=BytesIO(pdf_content)
    reader = PdfReader(stream)

    entity_name=get_entity_name(reader)
    full_pdf_text=get_pdf_text(reader)

    return [entity_name,full_pdf_text]


def get_entity_name(reader):
    try:
        page = reader.pages[0]
        page_text=page.extract_text().replace("\n","")
        
        starting_index=head_pattern.search(page_text).end()
        ending_index=foot_pattern.search(page_text).start()

        return page_text[starting_index+1:ending_index]
    except Exception:
        return ""    


def get_pdf_text(reader):
    full_pdf_text=""
    for page in reader.pages:
        full_pdf_text+=page.extract_text()
        full_pdf_text+="\n\n"
    return full_pdf_text

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


