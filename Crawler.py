import requests
import UrlList
import time, os
from bs4 import BeautifulSoup

requests.adapters.DEFAULT_RETRIES = 5


class Crawler():
    def __init__(self, major):
        """
        :param major: (str) 要获得论文的专业 e.g.："cs"
        """
        # self.urls = []
        # if isinstance(url, str):
        #     self.urls.append(url)
        # elif isinstance(url, list):
        #     self.urls.extend(url)
        self.url = "https://arxiv.org/list/" + major + "/"

    # def download(self):
    #     for url in self.urls:
    #         response = requests.get(url)
    #         name = url.split('/')[-1]
    #         savePath = "/home/cheng/文档/paper/" + name
    #         print("downloading:" + name)
    #         with open(savePath, "wb") as file:
    #             file.write(response.content)
    #         time.sleep(5)

    def getMonthSubject(self, year, month):
        """
        获得某年某月所有的论文名字和主题
        :param year: (str) e.g.: "21"表示2021年
        :param month: (srt) e.g.: "08"表示8月
        :return: None
        """
        currentUrl = self.url + year + month + "?skip=0&show=2000"
        response = requests.get(currentUrl)
        soup = BeautifulSoup(response.text, "html.parser")
        currentPaper = 0  # 当前论文数
        sumPaper = int(soup.small.b.previous_sibling.split()[-2])  # 该年总的论文数
        print("开始获取" + month + "月的内容\n")
        while (currentPaper < sumPaper):
            time.sleep(5)
            if currentPaper != 0:
                currentUrl = self.url + year + month + "?skip=" + str(currentPaper) + "&show=2000"
                response = requests.get(currentUrl)
                soup = BeautifulSoup(response.text, "html.parser")
            titles = soup.find_all("div", class_="list-title mathjax")  # 获取所有标题所在的div
            subjects = soup.find_all("span", class_="primary-subject")  # 获取所有主题所在的span
            for i in range(len(titles)):
                savePath = "../arxiv/cs/20" + month + ".txt"
                with open(savePath, "a") as f:
                    f.write(titles[i].span.next_sibling.strip() + ";" + subjects[i].text + "\n")
            currentPaper += 2000

    def getYearSubject(self, year):
        """
        获取某年所有的论文名字和主题
        :param year: (str) e.g.: "21"表示2021
        :return: None
        """
        os.makedirs("../arxiv/cs/", exist_ok=True)
        for m in range(1, 13):
            month = str(m) if m >= 10 else "0" + str(m)
            self.getMonthSubject(year, month)


if __name__ == "__main__":
    majors = ["physics", "math", "cs"]
    if not os.path.isdir("../arxiv"):
        os.mkdir("../arxiv")
    crawler = Crawler("cs")
    crawler.getYearSubject("20")
    # url = UrlList.getUrlList("https://arxiv.org/list/cs.AI/recent")
    # print(url)
    # crawler = Crawler(url)
    # crawler.download()
