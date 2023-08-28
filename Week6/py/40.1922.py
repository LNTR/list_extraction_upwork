from bs4 import BeautifulSoup

import pandas as pd
import requests
import time


FILE_NAME = "40.1922"

columns = ["State v. With Case Number","Type","PDF Url","Year"]

df = pd.DataFrame(columns = columns)


BASE_URL="https://www.ok.gov"
API_URL=f"{BASE_URL}/okdocc/Rules_&_Actions/Enforcement_Actions/index.html"

session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",}
    )


def main():

    response = get_response(API_URL)
    if response.status_code == 200:
        html = response.content.decode("utf-8")
       
        add_data_to_df(html)
        
    else:
        print(f"Error code {response.status_code}")

    
    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8')


def add_data_to_df(html):
    
    soup = BeautifulSoup(html,"lxml")
    div=soup.find(class_="cms_editor_content")
    p_list= div.find_all("p",class_="mzero")
    year=2023
    for p in p_list[1:]:
        if not p.find("a"):
            year=p.text.strip().split(" ")[-1]
            year=year.replace("Orders ","")
            if year=="":
                year="2013"
        else:
            row_data=get_row_data_list(p)
            row_data.append(year)
            df.loc[len(df)+1] = row_data


        
def get_row_data_list(p:BeautifulSoup):
    row_value_list=[]
    
    name=get_name_with_case_number(p)
    type=get_type(p)
    pdf_url=get_pdf_url(p)


    row_value_list.append(name)
    row_value_list.append(type)
    row_value_list.append(pdf_url)


    return row_value_list


def get_name_with_case_number(p):
    p_text=p.text.strip()

    if "consent" in p_text.lower():
        p_text= p_text.replace("Consent Order","")
    elif "final agency" in p_text:
        p_text= p_text.replace("Final Agency","")
    
    p_text=p_text.replace(";","")
    p_text=p_text.replace(",","")

    p_text=p_text.replace("State v. ","")
    return p_text


def get_pdf_url(p):
    resource_path=p.a["href"]
    pdf_url=f"{BASE_URL}{resource_path}"
    return pdf_url

def get_type(p):
    p_text=p.text.strip().lower()
    if "consent" in p_text:
        return "Consent Order"
    elif "final agency" in p_text:
        return "Final Agency"
    return ""

def get_response(url,*args,**kwargs):
    try:
        response = session.post(url,*args,**kwargs)
        return response
    except Exception as e:
        print(f"Error {e}\n Retrying in 5s")
        time.sleep(2)
        return get_response(url,*args,**kwargs)

if __name__ == "__main__":
    main()


