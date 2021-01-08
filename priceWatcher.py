import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"
}


class WebpageScraper:
    def __init__(self, URL):
        self.URL = URL

    def printItems(self) -> None:
        return


class NeweggScraper(WebpageScraper):
    def __init__(self, URL):
        super().__init__(URL)

    def isInStock(self, item) -> bool:
        itemPromo = item.find("p", class_="item-promo")
        if not itemPromo:
            return True
        return False if itemPromo.text == "OUT OF STOCK" else True

    def getItemAttributes(self, item) -> tuple:
        itemTitleElement = item.find("a", class_="item-title")
        itemName = itemTitleElement.text

        currentPriceElement = item.find("li", class_="price-current")
        basePrice = currentPriceElement.find('strong').text
        if basePrice != "COMING SOON":
            decimalPrice = currentPriceElement.find('sup').text
            itemPrice = basePrice + decimalPrice
        else:
            itemPrice = "N/A"

        shippingPrice = item.find("li", class_="price-ship").text

        return (itemName, itemPrice, shippingPrice)

    def printItems(self) -> None:
        page = requests.get(self.URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        items = soup.find_all("div", class_="item-cell")

        items = list(filter(self.isInStock, items))
        items = list(map(self.getItemAttributes, items))

        items.sort(key=lambda x: x[1])

        # Print Item Table
        print("*" * 180)
        print("--- Newegg URL: {} ---\n".format(URL))
        if len(items) == 0:
            print("No items in stock")
            return
        row_format = "{:<150} {:<15} {:<15}"
        for (name, price, shipping) in items:
            print(row_format.format(name, price,  shipping))
        print("*" * 180)


# Newegg
# URL = "https://www.newegg.com/p/pl?LeftPriceRange=200+500&N=100007709%204841%208000%20601357282%20601321572%20601331379&PageSize=96"
URL = "https://www.newegg.com/p/pl?N=100007709%204841%208000&PageSize=96"


# Ebay Newegg
# URL = "https://www.ebay.com/str/Newegg/VGA/_i.html?_storecat=12816376018&_sop=16&rt=nc"


# Reddit Posts
# URL = "https://www.reddit.com/r/buildapcsales/new/"

x = NeweggScraper(URL)
x.printItems()
