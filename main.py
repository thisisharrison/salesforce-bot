from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from secrets import pw
import pdb

class SFBot:
    def __init__(self, username, password):
        self.driver = webdriver.Chrome('/Users/harrisonlau/chromedriver')
        self.driver.implicitly_wait(5)
        self.username = username
        
        self.driver.get("https://staging-eu01-lululemon.demandware.net/on/demandware.store/Sites-Site/default/ViewLogin-StartAM")
        
        self.driver.find_element_by_xpath("//button[contains(text(), 'Log In')]")\
            .click()
        
        self.driver.find_element_by_xpath("//input[@name=\"callback_0\"]")\
            .send_keys(username)
        
        self.driver.find_element_by_xpath('//input[@type="submit"]')\
            .click()
        
        self.driver.find_element_by_xpath("//input[@name=\"callback_1\"]")\
            .send_keys(password)
        
        self.driver.find_element_by_xpath('//input[@type="submit"]')\
            .click()

        """ Select Site """
        sites = self.driver.find_element_by_xpath('//select[@id="SelectedSiteID"]')
        self.driver.execute_script("""
                                   arguments[0].selectedIndex = "1";
                                   arguments[0].onchange();
                                   """, sites)
        
        print("Logged in as: ", username)

    def navProducts(self):
        self.driver.find_element(By.CSS_SELECTOR, ".merchant-tools-link .icon-menu-menu_down_arrow").click()
        
        self.driver.find_element(By.LINK_TEXT, "Products").click()
              
        sleep(5)
        
        self.driver.find_element_by_link_text('By ID')\
            .click()
          
        print("Product Page")
    
    def setCategories(self, products, categories):
        
        self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]")\
            .send_keys(products)
        
        print("Searching: ", products)
        
        self.driver.find_element_by_xpath('//button[@name=\"findIDList\"]')\
            .click()
        
        self.driver.find_element_by_xpath('//button[@name=\"EditAll\"]')\
            .click()
            
        print("Found: ", products)
        
        self.driver.find_element_by_xpath("//input[@value='AssignProductToCatalogCategory']")\
            .click()
        
        self.driver.find_element_by_xpath('//button[@name=\"selectAction\"]')\
            .click()
        
        self.driver.find_element_by_xpath('//*[@id="ext-gen77"]')\
            .click()
        
        sleep(5)
        
        search = self.driver.find_element_by_xpath("//input[@name=\"ext-comp-1009\"]")\
            .send_keys(categories)

        self.driver.find_element(By.ID, "ext-comp-1009").send_keys(Keys.ENTER)
        
        print("Categorizing: ", products)
        
        self.driver.find_element(By.CSS_SELECTOR, ".x-grid3-row-checker").click()
        
        self.driver.find_element(By.NAME, "selectAction").click()
        
        dropdown = self.driver.find_element_by_xpath('//select[@name="PrimaryCategoryUUID"]')
        
        options = dropdown.find_element_by_xpath("//option[contains(text(), 'lululemon')]")\
            .click()
        
        self.driver.find_element_by_xpath('//button[@name="assignProductsAndReturn"]')\
            .click()
            
        print("Primary Categorized: %s > %s" % (products, categories))
            
    def changeAttribute(self, products):
        
        string_products = ", ".join(products)
        
        self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]")\
            .send_keys(string_products)
                       
        self.driver.find_element_by_xpath('//button[@name=\"findIDList\"]')\
            .click()
        
        # self.driver.find_element_by_xpath('//button[@value="All"]')\
        #     .click()
            
        product = products[0]
        
        el = self.driver.find_element_by_xpath("//a[contains(text(),'{}')]".format(product))
        
        url = el.get_attribute('href')
        
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(url)
        print("Opened new Tab")

        lang = self.driver.find_element_by_xpath('//select[@name="LocaleID"]')

        self.driver.execute_script("""arguments[0].selectedIndex = "23"; arguments[0].onchange();""", lang)

        print("Language Selected")

        self.driver.find_element_by_xpath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/table[2]/tbody/tr/td[1]/table/tbody/tr[3]/td/table/tbody/tr/td[2]/p/a').click()
        
        print("Unlocked")

        name = self.driver.find_element_by_xpath('//*[@id="Metaf070c9f07840c78a8b2edc1902_Container"]/input')
        name.clear()
        name.send_keys('Align Super High-Rise Pant *26"')

        self.driver.find_element_by_xpath("//button[contains(text(), 'Apply')]").click()
        print("Applied")

        self.driver.close()

        self.driver.switch_to.window(self.driver.window_handles[1])


    
    def deletePrice(self, skus):
        self.driver.find_element(By.CSS_SELECTOR, ".merchant-tools-link .icon-menu-menu_down_arrow").click()
        
        self.driver.find_element(By.LINK_TEXT, "Price Books").click()
        
        print("Price Book Page")
        
        print("Searching: ",skus)
        
        print("Found: ",skus)
        
        print("Deleting: ", skus)
        
        print("Deleted: ", skus)
        
        pass

products = ["LW5CYWA",
"LW5CWRA",
"LW5BYKA"
]
      
my_bot = SFBot('hlau2@lululemon.com', pw)

my_bot.navProducts()

my_bot.changeAttribute(products)

# my_bot.setCategories('prod1410121', 'women-tops-tanks')

# my_bot.deletePrice('113126055')



