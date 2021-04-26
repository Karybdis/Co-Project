import requests
import UrlList
import time, os
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

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
        os.makedirs("../arxiv/" + major, exist_ok=True)

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
        for m in range(1, 3):
            month = str(m) if m >= 10 else "0" + str(m)
            self.getMonthSubject(year, month)

    def getMonthSubjectProp(self, year, month):
        """
        获取某年某月所有的论文主题的占比
        :param year: (str) e.g.: "21"表示2021年
        :param month: (srt) e.g.: "08"表示8月
        :return: nums:(list[int])
                 labels:(list[str])
        """
        with open("../arxiv/cs/" + year + month + ".txt") as f:
            lines = f.readlines()
        sum = len(lines)  # 总的主题数
        subjectDict = {}
        for line in lines:
            subject = line.split(";")[-1].strip()
            subjectDict[subject] = subjectDict.get(subject, 0) + 1
        return self.getLabelsAndNum(subjectDict, sum)

    def getYearSubjectProp(self, year):
        """
        获取某年所有的论文主题的占比
        :param year: (str) e.g.: "21"表示2021年
        :return: nums:(list[int])
                 labels:(list[str])
        """
        subjectDict = {}
        sum = 0
        for m in range(1, 13):
            month = str(m) if m >= 10 else "0" + str(m)
            with open("../arxiv/cs/" + year + month + ".txt") as f:
                lines = f.readlines()
            sum += len(lines)
            for line in lines:
                subject = line.split(";")[-1].strip()
                subjectDict[subject] = subjectDict.get(subject, 0) + 1
        return self.getLabelsAndNum(subjectDict, sum)

    def getLabelsAndNum(self, subjectDict, sum):
        """
        获取画圆饼图所需的主题标签和每个主题对应的占比
        :param subjectDict: (dict[str:int])　存放主题和对应数量
        :param sum: (int) 主题总量
        :return: nums:(list[int])
                 labels:(list[str])
        """
        subjectNum = sorted(subjectDict.items(), key=lambda a: -a[1])  # 根据主题数量逆序排序
        labels = []
        nums = []
        cur = 0
        for label, num in subjectNum:
            labels.append(label)
            nums.append(num)
            cur += num
            if sum - cur < num or num / sum < 0.03:  # 剩下的主题单个占比过少，全部归为Others
                labels.append("Others")
                nums.append(sum - cur)
                break
        return nums, labels

    def searchPapreByTitle(self, title):
        """
        根据题目搜索论文
        :param title: (str) 论文题目
        :return: author: (list) 作者
                 abstract: (str) 摘要
                 subject: (str) 主题
        """
        title = self.replaceSign(title)
        words = title.split(" ")
        title = ""
        if (len(words) > 0):
            title += words[0]
        for i in range(1, len(words)):
            title += "+" + words[i]
        url = "https://arxiv.org/search/?query=" + title + "&searchtype=title&abstracts=show&order=&size=25"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        id = soup.find("p", class_="list-title is-inline-block").find("a").text[6:]
        return self.searchPaperByID(id)

    def searchPaperByID(self, id):
        """
        根据arxiv ID搜索论文
        :param id: (str) arxiv ID
        :return: author: (list) 作者
                 abstract: (str) 摘要
                 subject: (str) 主题
        """
        url = "https://arxiv.org/abs/" + id
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        authors = []
        a = soup.find("div", class_="authors").find_all("a")
        for e in a:
            authors.append(e.text)
        abstract = soup.find("blockquote").text.replace("\n", " ").strip()
        subject = soup.find("span", class_="primary-subject").text
        return authors, abstract, subject

    def replaceSign(self, title):
        """
        将题目中的特殊字符替换
        :param title: (str) 论文题目
        :return: title: (str) 替换后的论文题目
        """
        title = title.replace("(", "%28").replace(")", "%29").replace(":", "%3A")
        return title


if __name__ == "__main__":
    majors = ["physics", "math", "cs"]
    if not os.path.isdir("../arxiv"):
        os.mkdir("../arxiv")
    crawler = Crawler("cs")
    # crawler.getYearSubject("20")
    # nums,labels=crawler.getMonthSubjectProp("20","03")
    authors, abstract, subject = crawler.searchPapreByTitle(
        "MetaHTR: Towards Writer-Adaptive Handwritten Text Recognition")
    print(authors, "\n", abstract, "\n", subject)
    # nums, labels = crawler.getYearSubjectProp("20")
    # plt.pie(nums, labels=labels, autopct="%.2f%%")
    # plt.show()
