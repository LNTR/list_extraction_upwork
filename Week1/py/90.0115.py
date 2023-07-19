from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

FILE_NAME="90.0115"


payload={
    "menuNo":"400029",
    "englsFncEngnName":"",
    "fnltCtgryCode":"0605",
}
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}
df=pd.DataFrame({"Name":[],"Mobile No":[]})



URL="https://www.fnhubkorea.kr/eng/sprvise/instt/list.do"

session=requests.Session()

def main():
    page_count=get_page_count()

    for page_index in range(1,page_count+1):
        payload["pageIndex"]=page_index
        response=get_response(URL,params=payload)
        if response.status_code==200:
            html=response.text
            add_data_to_df(html)
        else:
            print(f"Error code {response.status_code}")
    df.to_csv(f"./csv/{FILE_NAME}.csv",index=False,encoding='utf-8')

def get_page_count():
    page_count=0
    payload["pageIndex"]=1
    response=get_response(URL,params=payload)
    soup=BeautifulSoup(response.text,"lxml")
    pagination_ul=soup.find("ul",class_="pagination")
    for li in pagination_ul.find_all("li"):
        if ("class" in li.attrs.keys()):
            if not("disabled" in li["class"]):
                page_count+=1
        else:
            page_count+=1
    return page_count

    
def add_data_to_df(html):
    
    soup=BeautifulSoup(html,"lxml")
    directory_list_soup=soup.find(class_="directory-list2")
    for li in directory_list_soup.ul.find_all("li"):
        company_name=li.strong.text.strip()
        telephone_no=li.find("a").text.strip()
        df.loc[len(df)+1]={"Name":company_name,
                   "Mobile No":telephone_no
                   }

    


def get_response(url,*args,**kwargs):
    try:
        response=session.get(url,*args,**kwargs)
        return response
    except Exception as e:
        print(f"Error {e}\n Retrying in 5s")
        time.sleep(2)
        return get_response(url,*args,**kwargs)


if __name__=="__main__":
    main()


