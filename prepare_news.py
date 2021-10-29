from bs4 import BeautifulSoup
import requests


class PrepareNews:
    def __init__(self):
        self.response = requests.get("https://news.ycombinator.com/")
        self.yc_webpage = self.response.text
        self.article_texts = []
        self.article_links = []
        self.create_soup()

    def create_soup(self):
        soup = BeautifulSoup(self.yc_webpage, "html.parser")
        self.article_texts = [
            (article_tag.getText()).encode("utf-8", "strict")
            for article_tag in soup.findAll(name="a", class_="storylink")
        ]
        self.article_links = [
            (article_tag.get("href")).encode("utf-8", "strict")
            for article_tag in soup.findAll(name="a", class_="storylink")
        ]

    def create_news(self):
        list_news = [
            {
                "a_text": self.article_texts[index],
                "a_link": self.article_links[index],
            }
            for index in range(10)
        ]
        return list_news


if __name__ == "__main__":
    pn = PrepareNews()
    news = pn.create_news()
    print(news)
