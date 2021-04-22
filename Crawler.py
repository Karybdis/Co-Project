import requests
import UrlList
import time
requests.adapters.DEFAULT_RETRIES = 5

class Crawler():
    def __init__(self, url):
        self.urls = []
        if isinstance(url, str):
            self.urls.append(url)
        elif isinstance(url, list):
            self.urls.extend(url)

    def download(self):
        for url in self.urls:
            response = requests.get(url)
            name = url.split('/')[-1]
            savePath = "/home/cheng/文档/paper/" + name
            print("downloading:" + name)
            with open(savePath, "wb") as file:
                file.write(response.content)
            time.sleep(5)


if __name__ == "__main__":
    #crawler = Crawler("https://arxiv.org/pdf/2104.10651.pdf")
    url = UrlList.getUrlList("https://arxiv.org/list/cs.AI/recent")
    print(url)
    crawler = Crawler(url)
    crawler.download()
