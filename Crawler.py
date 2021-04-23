import requests
import UrlList
import time
from bs4 import BeautifulSoup

requests.adapters.DEFAULT_RETRIES = 5


class Crawler():
    def __init__(self, url):
        # self.urls = []
        # if isinstance(url, str):
        #     self.urls.append(url)
        # elif isinstance(url, list):
        #     self.urls.extend(url)
        self.url = url

    # def download(self):
    #     for url in self.urls:
    #         response = requests.get(url)
    #         name = url.split('/')[-1]
    #         savePath = "/home/cheng/文档/paper/" + name
    #         print("downloading:" + name)
    #         with open(savePath, "wb") as file:
    #             file.write(response.content)
    #         time.sleep(5)

    def getSubject(self):
        currentUrl = self.url + "?skip=0&show=2000"
        response = requests.get(currentUrl)
        soup = BeautifulSoup(response.text, "html.parser")
        currentPaper = 0  # 当前论文数
        sumPaper = int(soup.small.b.previous_sibling.split()[-2])  # 该年总的论文数
        while (currentPaper < sumPaper):
            time.sleep(5)
            if currentPaper != 0:
                currentUrl = self.url + "?skip=" + str(currentPaper) + "&show=2000"
                response = requests.get(currentUrl)
                soup = BeautifulSoup(response.text, "html.parser")
            titles = soup.find_all("div", class_="list-title mathjax")  # 获取所有标题所在的div
            subjects = soup.find_all("span", class_="primary-subject")  # 获取所有主题所在的span
            for i in range(len(titles)):
                with open("./save.txt", "a") as f:
                    f.write(titles[i].span.next_sibling.strip() + ";" + subjects[i].text + "\n")
            currentPaper += 2000


if __name__ == "__main__":
    major = ["physics", "math", "cs"]
    crawler = Crawler("https://arxiv.org/list/cs/2001")
    crawler.getSubject()
    # url = UrlList.getUrlList("https://arxiv.org/list/cs.AI/recent")
    # print(url)
    # crawler = Crawler(url)
    # crawler.download()
