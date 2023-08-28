from bs4 import BeautifulSoup

import pandas as pd
import requests
import time


FILE_NAME = "40.1924"

columns = ["Name","Case Number" ,"Type of Business","Action","PDF Url","Date"]

df = pd.DataFrame(columns = columns)


BASE_URL="https://dfr.oregon.gov"
API_URL=f"{BASE_URL}/_vti_bin/Lists.asmx"

payload="<soap:Envelope xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:xsd='http://www.w3.org/2001/XMLSchema' xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'><soap:Body><GetListItems xmlns='http://schemas.microsoft.com/sharepoint/soap/'><listName>AdminOrders</listName><viewName></viewName><query><Query>  <Where> <And> <Geq><FieldRef Name='DFRYear' /><Value Type='Number'>1900</Value></Geq> <Leq><FieldRef Name='DFRYear' /><Value Type='Number'>2100</Value></Leq></And></Where> <OrderBy><FieldRef Name='DFROrderDate' Ascending='FALSE'></FieldRef></OrderBy> </Query></query><viewFields>  <ViewFields Properties='True' >  <FieldRef Name='Title' />  <FieldRef Name='DFRAction' />  <FieldRef Name='DFRType' />  <FieldRef Name='DFRName' />  <FieldRef Name='DFROrderDate' />  <FieldRef Name='DFRLocation' />  <FieldRef Name='DFRProgramArea' />  <FieldRef Name='DFRCaseNumber' />  <FieldRef Name='DFRYear' />  <FieldRef Name='DFRType' /> </ViewFields></viewFields><rowLimit>10000</rowLimit><queryOptions><QueryOptions><ViewAttributes Scope='Recursive' /></QueryOptions></queryOptions></GetListItems></soap:Body></soap:Envelope>"


session = requests.Session()

session.headers.update(
    {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "content-type": "text/xml; charset=utf-8",
        }
    )


def main():

    response = get_response(API_URL,data=payload)
    if response.status_code == 200:
        html = response.content.decode("utf-8")
       
        add_data_to_df(html)
        
    else:
        print(f"Error code {response.status_code}")

    
    df.to_csv(f"./csv/{FILE_NAME}.csv",index = False,encoding = 'utf-8')


def add_data_to_df(html):
    
    soup = BeautifulSoup(html,features="xml")
    row_list=soup.find_all("z:row")
    for row in row_list:
        row_data=get_row_data_list(row)
        df.loc[len(df)+1] = row_data


        
def get_row_data_list(row:BeautifulSoup):
    row_value_list=[]
    
    name=get_name(row)
    case_number=get_case_number(row)

    type_of_business=get_business_type(row)
    action=get_action_type(row)
    pdf_url=get_pdf_url(row)
    date=get_date(row)


    row_value_list.append(name)
    row_value_list.append(case_number)
    row_value_list.append(type_of_business)
    row_value_list.append(action)
    row_value_list.append(pdf_url)
    row_value_list.append(date)

    return row_value_list


def get_case_number(row):
    if "ows_DFRCaseNumber" in row.attrs.keys():
        return row["ows_DFRCaseNumber"]
    return ""
def get_name(row):
    if "ows_DFRName" in row.attrs.keys():
        return row["ows_DFRName"]

    return row["ows_Title"]

def get_business_type(row):
    if "ows_DFRProgramArea" in row.attrs.keys():
        return row["ows_DFRProgramArea"].split("#")[-1]
    return ""

def get_pdf_url(row):
    resource_path=row["ows_FileRef"].split("#")[-1]
    pdf_url=f"{BASE_URL}/{resource_path}"
    return pdf_url

def get_date(row):
    
    if "ows_DFROrderDate" in row.attrs.keys():
        date=row["ows_DFROrderDate"]
    else:
        date=""

    return date

def get_action_type(row):
    if "ows_DFRAction" in row.attrs.keys():
        return row["ows_DFRAction"]
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


