import requests
from typing import List
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

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
    def __init__(self, URL: str):
        super().__init__()
        self.URL = URL
        self.items = self.getItemsFromURL(URL)
        self.rowFormat = "{:<75} {:<15} {:<15}"
        return

    @abstractmethod
    def getItemsSoup(self) -> BeautifulSoup:
        return

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

    def buildItem(self, itemSoup: BeautifulSoup) -> Item:
        return Item(self.parseForName(itemSoup), float(self.parseForPrice(itemSoup).replace(",", "")), self.parseForShipping(itemSoup))

    def printItemTable(self) -> None:
        print("*" * 180)
        print("--- Newegg URL: {} ---\n".format(self.URL))

        if len(self.items) == 0:
            print("No items in stock")
        else:
            for item in self.items:
                print(self.rowFormat.format(
                    item.name, str(item.price), item.shipping))

        print("*" * 180)


class NeweggScraper(WebpageScraper):
    def __init__(self, URL):
        super().__init__(URL)

    def getItemsSoup(self) -> BeautifulSoup:
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

        try:
            nameArr = itemTitleElement.text.split()
            lowerCaseNameArr = [x.lower() for x in nameArr]
            for brand in CARD_BRANDS:
                if brand in lowerCaseNameArr:
                    return " ".join(nameArr[:lowerCaseNameArr.index(brand)+3])
        except:
            return itemTitleElement.text

        return itemTitleElement.text

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


# Newegg
# URL = "https://www.newegg.com/p/pl?LeftPriceRange=200+500&N=100007709%204841%208000%20601357282%20601321572%20601331379&PageSize=96"
URL = "https://www.newegg.com/p/pl?N=100007709%204841%208000&PageSize=96"


# Ebay Newegg
# URL = "https://www.ebay.com/str/Newegg/VGA/_i.html?_storecat=12816376018&_sop=16&rt=nc"


# Reddit Posts
# URL = "https://www.reddit.com/r/buildapcsales/new/"

x = NeweggScraper(URL)
x.printItemTable()
