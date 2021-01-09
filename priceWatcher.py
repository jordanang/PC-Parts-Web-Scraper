import requests
from typing import List
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import time


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "DNT": "1",
    "Connection": "close",
    "Upgrade-Insecure-Requests": "1"
}

CARD_BRANDS = ["geforce", "radeon"]


class Item:
    def __init__(self, name: str, price: float, shipping: str):
        self.name = name
        self.price = price
        self.shipping = shipping
        return


class WebpageScraper(ABC):
    def __init__(self, URL: str, description: str):
        super().__init__()
        self.URL = URL
        self.items = self.getItemsFromURL(URL)
        self.rowFormat = "{:<100} {:<15} {:<15}"
        self.description = description
        return

    @abstractmethod
    def getItemsSoup(self) -> List[BeautifulSoup]:
        pass

    @abstractmethod
    def parseForStock(self, itemSoup: BeautifulSoup) -> bool:
        pass

    @abstractmethod
    def parseForName(self, itemSoup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def parseForPrice(self, itemSoup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def parseForShipping(self, itemSoup: BeautifulSoup) -> str:
        pass

    def getItemsFromURL(self, URL) -> List[Item]:
        itemsSoup = self.getItemsSoup()
        itemsSoup = list(filter(self.parseForStock, itemsSoup))
        items = list(map(self.buildItem, itemsSoup))
        items.sort(key=lambda x: x.price, reverse=True)
        return items

    @staticmethod
    def getShortenedGraphicsCardName(name: str) -> str:
        nameArr = name.split()
        lowerCaseNameArr = [x.lower() for x in nameArr]
        for brand in CARD_BRANDS:
            if brand in lowerCaseNameArr:
                return " ".join(nameArr[:lowerCaseNameArr.index(brand)+4])

        return ""

    def buildItem(self, itemSoup: BeautifulSoup) -> Item:
        return Item(self.parseForName(itemSoup), float(self.parseForPrice(itemSoup).replace(",", "")), self.parseForShipping(itemSoup))

    def printItemTable(self) -> None:
        print("*" * 120)

        print("{:14}{}\n{:<14}{}\n".format(
            "Description: ", self.description, "URL: ", self.URL))

        if len(self.items) == 0:
            print("No items in stock")
        else:
            for item in self.items:
                print(self.rowFormat.format(
                    item.name, str(item.price), item.shipping))


class NeweggScraper(WebpageScraper):
    def __init__(self, URL: str, description: str):
        super().__init__(URL, description)

    def getItemsSoup(self) -> List[BeautifulSoup]:
        page = requests.get(self.URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup.find_all("div", class_="item-cell")

    def parseForStock(self, itemSoup: BeautifulSoup) -> bool:
        itemPromo = itemSoup.find("p", class_="item-promo")
        return False if itemPromo and itemPromo.text == "OUT OF STOCK" else True

    def parseForName(self, itemSoup: BeautifulSoup) -> str:
        itemTitleElement = itemSoup.find("a", class_="item-title")

        if not itemTitleElement:
            return ""

        shortenedName = WebpageScraper.getShortenedGraphicsCardName(
            itemTitleElement.text)

        return shortenedName if shortenedName != "" else itemTitleElement.text

    def parseForPrice(self, itemSoup: BeautifulSoup) -> str:
        currentPriceElement = itemSoup.find("li", class_="price-current")
        basePriceElement = currentPriceElement.find('strong')
        if basePriceElement and basePriceElement.text != "COMING SOON":
            decimalPriceElement = currentPriceElement.find('sup')
            return basePriceElement.text + decimalPriceElement.text
        else:
            return ""

    def parseForShipping(self, itemSoup: BeautifulSoup) -> str:
        shippingPriceElement = itemSoup.find("li", class_="price-ship")
        return "" if not shippingPriceElement else shippingPriceElement.text


class EbaystoreScraper(WebpageScraper):
    def __init__(self, URL: str, description: str):
        super().__init__(URL, description)

    def getItemsSoup(self) -> List[BeautifulSoup]:
        page = requests.get(self.URL)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup.find_all("li", class_="s-item")

    def parseForStock(self, itemSoup: BeautifulSoup) -> bool:
        # Item would not be posted if not in stock
        return True

    def parseForName(self, itemSoup: BeautifulSoup) -> str:
        itemNameElement = itemSoup.find("h3", class_="s-item__title")
        if not itemNameElement:
            return ""

        shortenedName = WebpageScraper.getShortenedGraphicsCardName(
            itemNameElement.text)

        return shortenedName if shortenedName != "" else itemNameElement.text

    def parseForPrice(self, itemSoup: BeautifulSoup) -> str:
        itemPriceElement = itemSoup.find("span", class_="s-item__price")
        return "" if not itemPriceElement else itemPriceElement.text[1:]

    def parseForShipping(self, itemSoup: BeautifulSoup) -> str:
        itemShippingElement = itemSoup.find("span", class_="s-item__shipping")
        return "" if not itemShippingElement else itemShippingElement.text


SCRAPERS = [
    {
        "cls": EbaystoreScraper,
        "description": "Ebay Newegg store for graphics cards greater than $200",
        "url": "https://www.ebay.com/str/Newegg/VGA/_i.html?_storecat=12816376018&_sop=16&LH_BIN=1&rt=nc&_udlo=200",
    },
    {
        "cls": NeweggScraper,
        "description": "Newegg Listing for graphics cards between $200 and $500",
        "url": "https://www.newegg.com/p/pl?LeftPriceRange=200+500&N=100007709%204841%208000%20601357282%20601321572%20601331379&PageSize=96"
    }
]


def main():
    while True:
        for scraper in SCRAPERS:
            cls, description, url = scraper["cls"], scraper["description"], scraper["url"]
            cls(url, description).printItemTable()
        print("*" * 40, " UPDATED: ", time.ctime(), " ", "*" * 41)
        time.sleep(60)


if __name__ == "__main__":
    main()
