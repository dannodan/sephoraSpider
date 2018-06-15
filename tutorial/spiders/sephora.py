import scrapy
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class SephoraSpider(scrapy.Spider):
    name = "sephora"

    def start_requests(self):

        self.driver = webdriver.Firefox()

        urls = [
            'https://www.sephora.com/shop/face-makeup?pageSize=1000'
            # 'https://www.sephora.com/shop/cheek-makeup?pageSize=2000',
            # 'https://www.sephora.com/shop/eye-makeup?pageSize=2000',
            # 'https://www.sephora.com/shop/lips-makeup?pageSize=2000',
            # 'https://www.sephora.com/shop/makeup-applicators?pageSize=2000',
            # 'https://www.sephora.com/shop/makeup-accessories?pageSize=2000',
            # 'https://www.sephora.com/shop/face-makeup?pageSize=2000',
            # 'https://www.sephora.com/shop/nail-makeup?pageSize=2000',
            # 'https://www.sephora.com/shop/clean-makeup?pageSize=2000',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.crawlProducts)

    def crawlProducts(self, response):
        self.driver.get(response.url)
        try:
            cancelButton = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, \
            '//div[@data-comp="SignInModal Modal"]//div[@data-comp="ModalFooter Box"]//button[@data-comp="ButtonOutline Button"]')))
        except TimeoutError:
            print("QUE CALIGUEVAAAAAAA")
        cancelButton.click()
        try:
            lazyProductsLoad = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, \
            '//div[@data-comp="ProductGrid"]//a[@data-comp="LazyLoad ProductItem"]')))
        except TimeoutError:
            print("QUE CALIGUEVAAAAAAA")
        last_height = self.driver.execute_script("return window.scrollY;")
        while True:
            self.driver.execute_script("window.scrollByPages(1);")
            height = self.driver.execute_script("return window.scrollY;")
            if height == last_height:
                break
            last_height = height
        products = self.driver.find_elements_by_xpath('//div[@data-comp="ProductGrid"]//a[@data-comp="ProductItem"]')
        lazyProducts = self.driver.find_elements_by_xpath('//div[@data-comp="ProductGrid"]//a[@data-comp="LazyLoad ProductItem"]')
        products.extend(lazyProducts)
        for product in products:    
            productUrl = product.get_attribute("href")
            yield scrapy.Request(url=productUrl, callback=self.seleniumScraping)
        self.driver.close()

    def seleniumScraping(self, response):
        self.driver.get(response.url)
        # try:
        #     cancelButton = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, \
        #     '//div[@data-comp="SignInModal Modal"]//div[@data-comp="ModalFooter Box"]//button[@data-comp="ButtonOutline Button"]')))
        # except TimeoutError:
        #     print("QUE CALIGUEVAAAAAAA")
        # cancelButton.click()
        swatches = self.driver.find_elements_by_xpath('//div[@data-comp="ProductPage Container Box"]'\
            '//div[@data-comp="Swatches Box"]//div[@data-comp="ProductSwatchItem"]/button')
        productPresentations = []
        for swatch in swatches:
            swatch.click()
            product = self.processProduct()
            productPresentations.append(product)
        yield productPresentations

    def processProduct(self):
        productId = (self.driver.find_element_by_xpath('//div[@data-comp="ProductPage Container Box"]//div[@data-comp="Grid Flex Box"]'\
            '//div[@data-comp="SizeAndItemNumber Box"]')).text
        productBrand = (self.driver.find_element_by_xpath('//div[@data-comp="ProductPage Container Box"]//div[@data-comp="GridCell Box"]'\
            '//h1[@data-comp="DisplayName Text"]/a/span')).text
        productName = (self.driver.find_element_by_xpath('//div[@data-comp="ProductPage Container Box"]//div[@data-comp="GridCell Box"]'\
            '//h1[@data-comp="DisplayName Text"]/span')).text
        productPrice = (self.driver.find_element_by_xpath('//div[@data-comp="ProductPage Container Box"]//div[@data-comp="Grid Flex Box"]'\
            '//div[@data-comp="Price Box"]')).text
        # productImages = self.driver.find_elements_by_xpath('//div[@data-comp="HeroMediaList"]/div[@data-comp="Carousel"]')

        output = {
            "id": productId,
            "name": productName,
            "brand": productBrand,
            "price": productPrice,
            # "images": self.processImages(productImages)
        }

        return output

    def processImages(self, images):
        imageList = []
        for image in images:
            imageList.append(image.get_attribute('xlink:href'))

        return imageList