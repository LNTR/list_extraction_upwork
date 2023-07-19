from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import re

FILE_NAME = "90.0116"



headers  =  {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}
columns = ["Name","Cell No","Tel No","Fax","Email","Website","Address"]

df = pd.DataFrame(columns = columns)

international_insurance_entity_type_list=[
    "Allied Reinsurance Companies",
    "Captive Insurance Companies",
    "General & Reinsurance Companies",
    "General Insurance Companies",
    "Long Term Insurance Companies",
    "Reinsurance Companies",
    "Insurance Brokers"
]

pattern_list = [
            re.compile(r"Cell:\s?.*\n",re.IGNORECASE),
            re.compile(r"Tel:\s?.*\n",re.IGNORECASE),
            re.compile(r"Fax:\s?.*\n",re.IGNORECASE),
            re.compile(r"E\-?mail:.+\n",re.IGNORECASE),
            re.compile(r"Website:.+\n",re.IGNORECASE),
            ]


URL = "https://www.nevisfsrc.com/regulated-entities/"

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
    panel_heading_list = soup.find_all(class_ = "vc_tta-panel-heading")
    for panel_heading in panel_heading_list:
        company_name = panel_heading.h4.text.strip()
        panel_body = panel_heading.next_sibling

        if company_name in international_insurance_entity_type_list:
            company_name_list=get_internation_entity_names(panel_body)
            add_company_name_list_to_df(company_name_list)
            
        else:
            body_data = get_body_data_list(panel_body)
            df.loc[len(df)+1] = [company_name]+body_data
                


def get_internation_entity_names(panel_body):
    company_name_list=[]
    for li in panel_body.find("ul").find_all("li"):
        company_name_list.append(li.text.strip())
    return company_name_list

def add_company_name_list_to_df(company_name_list):
    for company_name in company_name_list:
        df.loc[len(df)+1] = [company_name]+[None]*6


def get_body_data_list(soup):

    p = soup.find("p")
    if p:
        p=p.text
    else:
        p=""
    p = p.replace("<p>","")
    p = p.replace("</p>","")
    p = p+"\n"

    match_list = []

    for pattern in pattern_list:

        pattern_match = pattern.search(p)
        
        if pattern_match:
            match_value = pattern_match.group(0)
            p = p.replace(match_value,"")
            match_value = get_normalized_match_value(match_value)
            match_list.append(match_value)
        else:
            match_list.append(None)

    match_list.append(p)

    return match_list

def get_normalized_match_value(match_value):
    match_value = match_value.split(":")[-1].strip()
    match_value = match_value.replace("<br/>","")

    if match_value.startswith(" "):
        match_value = match_value[1:]
    if match_value.endswith(" "):
        match_value = match_value[:-1]
    if match_value.startswith("//"):
        match_value = match_value[2:]


    return match_value
    

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


