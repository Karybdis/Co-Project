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
            time.sleep(3)
            if currentPaper != 0:
                currentUrl = self.url + year + month + "?skip=" + str(currentPaper) + "&show=2000"
                response = requests.get(currentUrl)
                soup = BeautifulSoup(response.text, "html.parser")
            titles = soup.find_all("div", class_="list-title mathjax")  # 获取所有标题所在的div
            subjects = soup.find_all("span", class_="primary-subject")  # 获取所有主题所在的span
            for i in range(len(titles)):
                savePath = "../arxiv/cs/" + year + month + ".txt"
                with open(savePath, "a") as f:
                    f.write(titles[i].span.next_sibling.strip() + ";" + subjects[i].text + "\n")
            currentPaper += 2000

    def getYearSubject(self, year):
        """
        获取某年所有的论文名字和主题
        :param year: (str) e.g.: "21"表示2021
        :return: None
        """
        for m in range(1, 13):
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

    def searchPaperByTitle(self, title, download=False):
        """
        根据题目搜索论文
        :param title: (str) 论文题目
        :return: url: (str) 论文url地址
                 info: (list[
                 id: (str) arxiv ID
                 title: (str) 题目
                 author: (list) 作者
                 abstract: (str) 摘要
                 subject: (str) 主题
                 ])
        """
        title = self.replaceSign(title)
        words = title.split(" ")
        title = ""
        if len(words) > 0:
            title += words[0]
        for i in range(1, len(words)):
            title += "+" + words[i]
        url = "https://arxiv.org/search/?query=" + title + "&searchtype=title&abstracts=show&order=&size=25"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("span", class_="is-warning") is not None:
            if download:
                return ""
            else:
                assert soup.find("span", class_="is-warning") is None, "no result for search"
        if download:
            id = soup.find("p", class_="list-title is-inline-block").find("a").text[6:]
            return "https://arxiv.org/pdf/" + id + ".pdf"
        p_list = soup.find_all("p", class_="list-title is-inline-block")
        id_list = []
        for i in range(min(10, len(p_list))):
            id_list.append(p_list[i].find("a").text[6:])
        return self.searchPaperByID(id_list)

    def searchPaperByAuthor(self, author):
        """
        根据作者搜索论文
        :param author: (str) 作者
        :return: info: (list[
                 id: (str) arxiv ID
                 title: (str) 题目
                 author: (list) 作者
                 abstract: (str) 摘要
                 subject: (str) 主题
                 ])
        """
        words = author.split(" ")
        author = ""
        if len(words) > 0:
            author += words[0]
        for i in range(1, len(words)):
            author += "+" + words[i]
        url = "https://arxiv.org/search/?query=" + author + "&searchtype=author&abstracts=show&order=&size=25"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        assert soup.find("span", class_="is-warning") is None, "no result for search"
        p_list = soup.find_all("p", class_="list-title is-inline-block")
        id_list = []
        for i in range(min(10, len(p_list))):
            id_list.append(p_list[i].find("a").text[6:])
        return self.searchPaperByID(id_list)

    def searchPaperByAbstract(self, abstract):
        """
        根据摘要搜索论文
        :param abstract: (str) 摘要
        :return: info: (list[
                 id: (str) arxiv ID
                 title: (str) 题目
                 author: (list) 作者
                 abstract: (str) 摘要
                 subject: (str) 主题
                 ])
        """
        words = abstract.split(" ")
        abstract = ""
        if len(words) > 0:
            abstract += words[0]
        for i in range(1, len(words)):
            abstract += "+" + words[i]
        url = "https://arxiv.org/search/?query=" + abstract + "&searchtype=abstract&abstracts=show&order=&size=25"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        assert soup.find("span", class_="is-warning") is None, "no result for search"
        p_list = soup.find_all("p", class_="list-title is-inline-block")
        id_list = []
        for i in range(min(10, len(p_list))):
            id_list.append(p_list[i].find("a").text[6:])
        return self.searchPaperByID(id_list)

    def searchPaperByID(self, id_list):
        """
        根据arxiv ID搜索论文
        :param id_list: (list[str]) arxiv ID
        :return: info: (list[
                 id: (str) arxiv ID
                 title: (str) 题目
                 author: (list) 作者
                 abstract: (str) 摘要
                 subject: (str) 主题
                 ])
        """
        info = []
        for i in range(len(id_list)):
            id = id_list[i]
            url = "https://arxiv.org/abs/" + id
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find("h1", class_="title mathjax").span.next_sibling
            authors = []
            a = soup.find("div", class_="authors").find_all("a")
            for e in a:
                authors.append(e.text)
            abstract = soup.find("blockquote").text.replace("\n", " ").strip()
            subject = soup.find("span", class_="primary-subject").text
            dict = {"id": id, "title": title, "authors": authors, "abstract": abstract, "subject": subject}
            info.append(dict)
            time.sleep(0.5)
        with open("./sss.txt", 'w') as f:
            for i in range(len(id_list)):
                f.write(info[i]["id"] + "\n")
        return info

    def replaceSign(self, title):
        """
        将题目中的特殊字符替换
        :param title: (str) 论文题目
        :return: title: (str) 替换后的论文题目
        """
        title = title.replace("(", "%28").replace(")", "%29").replace(":", "%3A")
        return title

    def downloadPaperFromTxt(self, txtPath, savePath):
        """
        :param txtPath: (str) txt地址
        :param savePath: (str) 保存地址
        :return:Ｎone
        """
        with open(txtPath, 'r') as f:
            lines = f.readlines()
        urls = []
        for line in lines:
            time.sleep(3)
            url = self.searchPaperByTitle(line.strip(), True)
            if url != "":
                urls.append(url)
        self.download(urls, savePath)

    def downloadPaperFromInput(self, input,savePath):
        """
        :param input: (str) 下载的索引（１开始），逗号隔开　e.g.:"1,2,3,4"
        :param savePath: (str) 保存地址
        :return: None
        """
        nums = input.split(',')
        indices = set()
        urls=[]
        with open("./sss.txt", 'r') as f:
            lines = f.readlines()
        for num in nums:
            if num.isdigit() and int(num)<=len(lines):
                indices.add(int(num))
        for index in indices:
            url ="https://arxiv.org/pdf/" + lines[index-1].strip() + ".pdf"
            urls.append(url)
        self.download(urls,savePath)

    def download(self, urls, savePathRoot):
        """
        :param urls: (list[str]) pdf的url地址
        :param savePathRoot: (str) 保存地址
        :return:
        """
        os.makedirs(savePathRoot, exist_ok=True)
        for url in urls:
            response = requests.get(url)
            name = url.split('/')[-1]
            savePath = os.path.join(savePathRoot, name)
            print("downloading:" + name)
            with open(savePath, "wb") as file:
                file.write(response.content)
            time.sleep(3)


if __name__ == "__main__":
    majors = ["physics", "math", "cs", "q-bio", "q-fin", "stat"]
    # if not os.path.isdir("../arxiv"):
    #     os.mkdir("../arxiv")
    crawler = Crawler("cs")
    # crawler.getYearSubject("19")
    # nums,labels=crawler.getMonthSubjectProp("20","01")
    # info = crawler.searchPaperByAuthor(
    #     "Chengyue Jiang")
    # print(info)
    # nums, labels = crawler.getYearSubjectProp("20")
    # plt.pie(nums, labels=labels, autopct="%.2f%%")
    # plt.show()
    # crawler.downloadPaperFromTxt("/home/cheng/paper.txt", "/home/cheng/dlPaper")
    crawler.downloadPaperFromInput("1,2,3","/home/cheng/dlPaper")
