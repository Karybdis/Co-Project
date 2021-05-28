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
        self.major=major
        os.makedirs("../arxiv/" + major, exist_ok=True)

    def getYearMonthSubject(self, year, month):
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
        print("开始获取" + year + "年" + month + "月的内容\n")
        while (currentPaper < sumPaper):
            time.sleep(3)
            if currentPaper != 0:
                currentUrl = self.url + year + month + "?skip=" + str(currentPaper) + "&show=2000"
                response = requests.get(currentUrl)
                soup = BeautifulSoup(response.text, "html.parser")
            titles = soup.find_all("div", class_="list-title mathjax")  # 获取所有标题所在的div
            subjects = soup.find_all("span", class_="primary-subject")  # 获取所有主题所在的span
            for i in range(len(titles)):
                savePath = "../arxiv/"+self.major+"/" + year + month + ".txt"
                with open(savePath, "a") as f:
                    f.write(titles[i].span.next_sibling.strip() + ";" + subjects[i].text + "\n")
            currentPaper += 2000

    def getTimeQuantumSubject(self, startYear, startMonth, endYear, endMonth):
        """
        获取某个时间范围内的论文名字和主题
        :param startYear: (str | int) 开始年份，2018-2021
        :param startMonth: (str | int) 开始月份，2018-2021
        :param endYear: (str | int) 结束年份，01-12
        :param endMonth: (str | int) 结束月份，01-12
        :return: None
        """
        if isinstance(startYear, str):
            assert startYear.isdigit() and len(startYear) == 4
            startYear = int(startYear)
        if isinstance(endYear, str):
            assert endYear.isdigit() and len(endYear) == 4
            endYear = int(endYear)
        assert 2018 <= startYear <= 2021 and 2018 <= endYear <= 2021
        startYear -= 2000
        endYear -= 2000
        if isinstance(startMonth, str):
            assert startMonth.isdigit() and len(startMonth) == 2
            startMonth = int(startMonth)
        if isinstance(endMonth, str):
            assert endMonth.isdigit() and len(endMonth) == 2
            endMonth = int(endMonth)
        assert 1 <= startMonth <= 12 and 1 <= endMonth <= 12
        assert startYear < endYear or startYear == endYear and startMonth <= endMonth
        assert endYear < 21 or endYear == 21 and endMonth <= 5, "No Paper after 2021.05"
        for year in range(startYear, endYear + 1):
            if year == startYear:
                curStartMonth = startMonth
            else:
                curStartMonth = 1
            if year == endYear:
                curEndMonth = endMonth
            else:
                curEndMonth = 12
            for month in range(curStartMonth, curEndMonth + 1):
                self.getYearMonthSubject(str(year), str(month) if month >= 10 else "0" + str(month))

    def getYearMonthSubjectProp(self, year, month):
        """
        获取某年某月所有的论文主题的占比
        :param year: (str) e.g.: "21"表示2021年
        :param month: (srt) e.g.: "08"表示8月
        :return: nums:(list[int])   某个主题数量，逆序存储
                 labels:(list[str]) 某个主题标签，索引对应nums
        """
        with open("../arxiv/"+self.major+"/" + year + month + ".txt") as f:
            lines = f.readlines()
        sum = len(lines)  # 总的主题数
        subjectDict = {}
        for line in lines:
            subject = line.split(";")[-1].strip()
            subjectDict[subject] = subjectDict.get(subject, 0) + 1
        return self.getLabelsAndNum(subjectDict, sum)

    def getTimeQuantumSubjectProp(self, startYear, startMonth, endYear, endMonth):
        """
        获取某个时间段内所有的论文主题的占比
        :param startYear: (str) 开始年份，2018-2021
        :param startMonth: (str) 开始月份，2018-2021
        :param endYear: (str) 结束年份，01-12
        :param endMonth: (str) 结束月份，01-12
        :return: nums:(list[int])   某个主题数量，逆序存储
                 labels:(list[str]) 某个主题标签，索引对应nums
        """

        startYear = int(startYear) - 2000
        endYear = int(endYear) - 2000
        startMonth = int(startMonth)
        endMonth = int(endMonth)
        assert 1 <= startMonth <= 12 and 1 <= endMonth <= 12
        assert startYear < endYear or startYear == endYear and startMonth <= endMonth
        assert endYear < 21 or endYear == 21 and endMonth <= 5, "No Paper after 2021.05"
        subjectDict = {}
        sum = 0
        for year in range(startYear, endYear + 1):
            if year == startYear:
                curStartMonth = startMonth
            else:
                curStartMonth = 1
            if year == endYear:
                curEndMonth = endMonth
            else:
                curEndMonth = 12
            for month in range(curStartMonth, curEndMonth + 1):
                m = str(month) if month >= 10 else "0" + str(month)
                with open("../arxiv/"+self.major+"/" + str(year) + m + ".txt") as f:
                    lines = f.readlines()
                sum += len(lines)
                for line in lines:
                    subject = line.split(";")[-1].strip()
                    subjectDict[subject] = subjectDict.get(subject, 0) + 1
        return self.getLabelsAndNum(subjectDict, sum)

    def getTimeQuantumSubjectTrend(self, startYear, startMonth, endYear, endMonth):
        """
        获取某个时间段Top5主题的趋势
        :param startYear: (str) 开始年份，2018-2021
        :param startMonth: (str) 开始月份，2018-2021
        :param endYear: (str) 结束年份，01-12
        :param endMonth: (str) 结束月份，01-12
        :return: None
        """
        _, labels = self.getTimeQuantumSubjectProp(startYear, startMonth, endYear, endMonth)
        startYear = int(startYear) - 2000
        endYear = int(endYear) - 2000
        startMonth = int(startMonth)
        endMonth = int(endMonth)

        time = 0
        for year in range(startYear, endYear + 1):
            if year == startYear:
                curStartMonth = startMonth
            else:
                curStartMonth = 1
            if year == endYear:
                curEndMonth = endMonth
            else:
                curEndMonth = 12
            time += curEndMonth - curStartMonth + 1
        x = [i for i in range(time)]
        y = [[0 for _ in range(time)] for _ in range(time)]

        subjectIndex = {}
        for i in range(5):
            subjectIndex[labels[i]] = i
        time = 0
        xticks = []
        for year in range(startYear, endYear + 1):
            if year == startYear:
                curStartMonth = startMonth
            else:
                curStartMonth = 1
            if year == endYear:
                curEndMonth = endMonth
            else:
                curEndMonth = 12
            for month in range(curStartMonth, curEndMonth + 1):
                m = str(month) if month >= 10 else "0" + str(month)
                xticks.append(str(year) + m)
                with open("../arxiv/"+self.major+"/" + str(year) + m + ".txt") as f:
                    lines = f.readlines()
                for line in lines:
                    subject = line.split(";")[-1].strip()
                    if subject in subjectIndex:
                        y[subjectIndex[subject]][time] += 1
                time += 1
        for i in range(len(y)):
            plt.plot(x,y[i],label=labels[i])
        plt.xticks(x,xticks)
        plt.legend(bbox_to_anchor=(0,1.02),loc=3, borderaxespad=0)
        plt.show()


    def getLabelsAndNum(self, subjectDict, sum):
        """
        获取画圆饼图所需的主题标签和每个主题对应的占比
        :param subjectDict: (dict[str:int])　存放主题和对应数量
        :param sum: (int) 主题总量
        :return: nums:(list[int])   某个主题数量，逆序存储
                 labels:(list[str]) 某个主题标签，索引对应nums
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
                download (boolean) 标识符，当该方法被downloadPaperFromTxt调用时候为true
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
        pList = soup.find_all("p", class_="list-title is-inline-block")
        idList = []
        for i in range(min(10, len(pList))):
            idList.append(pList[i].find("a").text[6:])
        return self.searchPaperByID(idList)

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
        pList = soup.find_all("p", class_="list-title is-inline-block")
        idList = []
        for i in range(min(10, len(pList))):
            idList.append(pList[i].find("a").text[6:])
        return self.searchPaperByID(idList)

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
        pList = soup.find_all("p", class_="list-title is-inline-block")
        idList = []
        for i in range(min(10, len(pList))):
            idList.append(pList[i].find("a").text[6:])
        return self.searchPaperByID(idList)

    def searchPaperByID(self, id):
        """
        根据arxiv ID搜索论文
        :param id: (str | list[str]) arxiv ID
        :return: info: (list[
                 id: (str) arxiv ID
                 title: (str) 题目
                 author: (list) 作者
                 abstract: (str) 摘要
                 subject: (str) 主题
                 ])
        """
        idList = []
        if isinstance(id, list):
            idList = id
        elif isinstance(id, str):
            idList.append(id)
        info = []
        for i in range(len(idList)):
            id = idList[i]
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
            for i in range(len(idList)):
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
        从本地批量下载论文
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

    def downloadPaperFromInput(self, input, savePath):
        """
        从输入序号下载论文
        :param input: (str) 下载的索引（１开始），英文逗号隔开　e.g.:"1,2,3,4"
        :param savePath: (str) 保存地址
        :return: None
        """
        nums = input.split(',')
        indices = set()
        urls = []
        with open("./sss.txt", 'r') as f:
            lines = f.readlines()
        for num in nums:
            if num.isdigit() and int(num) <= len(lines):
                indices.add(int(num))
        for index in indices:
            url = "https://arxiv.org/pdf/" + lines[index - 1].strip() + ".pdf"
            urls.append(url)
        self.download(urls, savePath)

    def download(self, urls, savePathRoot):
        """
        下载论文
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
    # crawler.getTimeQuantumSubject("2019", "08", "2020", "03")
    # nums,labels=crawler.getYearMonthSubjectProp("20","01")
    # info = crawler.searchPaperByID(
    #     ["2012.15397", "2012.13501"])
    # print(info)
    # nums, labels = crawler.getTimeQuantumSubjectProp("2019", "08", "2020", "03")
    # plt.pie(nums, labels=labels, autopct="%.2f%%")
    # plt.show()
    crawler.getTimeQuantumSubjectTrend("2019", "08", "2019", "12")
    # crawler.downloadPaperFromTxt("/home/cheng/paper.txt", "/home/cheng/dlPaper")
    # crawler.downloadPaperFromInput("1,2,3","/home/cheng/dlPaper")
