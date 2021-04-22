import requests
from bs4 import BeautifulSoup

def getUrlList(url):
    response=requests.get(url)
    soup=BeautifulSoup(response.text,'html.parser')
    aLabels=soup.find_all("a",title="Download PDF")
    pdfUrlList=[]
    for aLabel in aLabels:
        href=aLabel["href"]
        pdfUrl="https://arxiv.org"+href+".pdf"
        pdfUrlList.append(pdfUrl)
    return pdfUrlList

if __name__ == "__main__":
    url = "https://arxiv.org/list/cs.AI/recent"
    print(getUrlList(url))