import requests
from bs4 import BeautifulSoup


class Item:
    def __init__(self, URL):
        self.URL = URL

    def getPrice(self) -> float:
        return

    def getPriceFormatted(self) -> str:
        return "Price: {:0.2f}".format(self.getPrice())

    def isInStock(self) -> bool:
        return


class NeweggItem(Item):
    def __init__(self, URL):
        super().__init__(URL)

    def getPrice(self) -> float:
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        currentPriceElement = soup.find("li", class_="price-current")
        basePriceElement = currentPriceElement.find('strong')
        decimalPriceElement = currentPriceElement.find('sup')
        return float(basePriceElement.text) + float(decimalPriceElement.text)

    def isInStock(self) -> bool:
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        productBuyElement = soup.find(id="ProductBuy")
        return len(productBuyElement.find_all('button')) == 0

# URL = "https://www.newegg.com/intel-pentium-d-925/p/N82E16819116440?Item=9SIA4MR6HF9832"
# URL = "https://www.newegg.com/amd-ryzen-5-5600x/p/N82E16819113666?Item=N82E16819113666"

# x = NeweggItem(URL)
# print(x.isInStock())
# x.getPriceFormatted()
