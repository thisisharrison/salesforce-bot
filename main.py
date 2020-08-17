from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import csv 
from secrets import pw
import pdb

class SFBot:
    def __init__(self, username, password):
        """ PERSONAL MAC """
        self.driver = webdriver.Chrome('/Users/harrisonlau/chromedriver')
        
        """ OFFICE WINDOWS """
        # self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
        
        self.username = username

        self.password = password
        
        self.driver.get("https://staging-eu01-lululemon.demandware.net/on/demandware.store/Sites-Site/default/ViewLogin-StartAM")
        
        self.driver.find_element_by_xpath("//button[contains(text(), 'Log In')]")\
            .click()
        
        self.login()

    def login(self):

        try:
        
            self.driver.find_element_by_xpath("//input[@name=\"callback_0\"]")\
                .send_keys(self.username)
            
            self.driver.find_element_by_xpath('//input[@type="submit"]')\
                .click()
            
            self.driver.find_element_by_xpath("//input[@name=\"callback_1\"]")\
                .send_keys(self.password)
            
            self.driver.find_element_by_xpath('//input[@type="submit"]')\
                .click()
        
        except:

            print("Retry logging in")
            self.login()

        """ Select Site """
        # Select first (Japan) 
        sites = self.driver.find_element_by_xpath('//select[@id="SelectedSiteID"]')
        self.driver.execute_script("""
                                   arguments[0].selectedIndex = "1";
                                   arguments[0].onchange();
                                   """, sites)
        
        print("Logged in as: ", self.username)
        
        sleep(3)

    def navProducts(self):
        
        try: 
            self.driver.find_element(By.CSS_SELECTOR, ".menu .merchant-tools-link > .menu-overview-link-icon").click()
        
            sleep(3)
                  
            self.driver.find_element_by_link_text('Products').click()
        
        except: 
            
            self.driver.find_element_by_link_text('Merchant Tools')\
                .click()
            
            self.driver.find_element_by_link_text('Products and Catalogs')\
                .click()
            
            self.driver.find_element_by_link_text('Products')\
                .click()
            
            print("Alternative Navigation")
        
        sleep(3)
        
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
            
    def changeAttribute(self, names):
        
        try: 
            while names:
                
                # Takes first pair, when finished pop(0)
                pair = names[0]
                print(pair)
                
                product = pair[0]
                attribute = pair[1]
            
                search = self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]")
                search.send_keys(product)
                               
                self.driver.find_element_by_xpath('//button[@name=\"findIDList\"]')\
                    .click()
                
                self.driver.find_element_by_link_text(product)\
                    .click()
                
                # If Search Multiple Products (separate function)
                # el = self.driver.find_element_by_xpath("//a[contains(text(),'{}')]".format(product))
                # url = el.get_attribute('href')
                # self.driver.switch_to.window(self.driver.window_handles[1])
                # self.driver.get(url)
                # print("Opened new Tab")
                # self.driver.close()
                # self.driver.switch_to.window(self.driver.window_handles[1])
    
                lang = self.driver.find_element_by_xpath('//select[@name="LocaleID"]')
                
                """ SELECT LANGUAGE """
                self.driver.execute_script("""arguments[0].selectedIndex = "7"; 
                                           arguments[0].onchange();""", lang)
        
                print("Language Selected")
        
                self.driver.find_element_by_xpath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/table[2]/tbody/tr/td[1]/table/tbody/tr[3]/td/table/tbody/tr/td[2]/p/a').click()
                
                print("Unlocked")
        
                name = self.driver.find_element_by_xpath('//*[@id="Metaf070c9f07840c78a8b2edc1902_Container"]/input')
                
                name.clear()
                
                name.send_keys(attribute)
        
                self.driver.find_element_by_xpath("//button[contains(text(), 'Apply')]").click()
                
                print("Applied")
                
                self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()
                
                done = names.pop(0)
                
                print("Remaining pairs: ", names)
                
        except:
            
            print('Error: Error Occurred')
            
            print('Error: Remaining Pairs: ', names)
            
            self.changeAttribute(names)
            

    def getCategoryMapping(self, filename):

        pCats = {}
        sCats = {}

        with open (filename, newline = '') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader: 
                master = row['master']
                primary = row['primaryCategory']
                secondary = [cat.strip() for cat in row['subCategories'].split(',')]

                if primary in pCats.keys():
                    pCats[primary].add(master)
                else: 
                    pCats[primary] = set([master])
                
                for sec in secondary:
                    if sec in sCats.keys():
                        sCats[sec].add(master)
                    else:
                        sCats[sec] = set([master])
                    
        print(pCats)
        print(sCats)
        

    def navPriceBook(self, priceBook):
     
        try: 
            self.driver.find_element(By.CSS_SELECTOR, ".menu .merchant-tools-link > .menu-overview-link-icon").click()
        
            sleep(3)
                  
            self.driver.find_element(By.LINK_TEXT, "Price Books").click()
        
        except: 
            
            self.driver.find_element_by_link_text('Merchant Tools')\
                .click()
            
            self.driver.find_element_by_link_text('Products and Catalogs')\
                .click()
            
            self.driver.find_element_by_link_text('Price Books')\
                .click()
            
            print("Alternative Navigation")
         
        self.driver.find_element_by_xpath('//button[@name="PageSize"]')\
            .click()
        
        try: 
        
            self.driver.find_element(By.LINK_TEXT, priceBook).click()
        
        except:
        
            self.driver.find_element_by_xpath("//input[@name=\"SearchTerm\"]").send_keys(priceBook)
            
            self.driver.find_element_by_xpath("//button[@name=\"simpleSearch\"]").click()
            
            self.driver.find_element(By.LINK_TEXT, priceBook).click()
            
        self.driver.find_element(By.LINK_TEXT, "Price Definitions").click() 
        
        self.driver.find_element(By.CSS_SELECTOR, "td:nth-child(3) > .perm_not_disabled").click()
        
    def deletePrice(self, skus):
                    
        search = self.driver.find_element_by_xpath("//input[@name=\"SearchTerm\"]")
        search.clear()

        print("Price Book Page")
        
        try: 
            while skus:
                
                # Takes first sku, when finish, pop(0); Need a error handler for if no search result
                sku = skus.pop(0)
        
                self.driver.find_element_by_xpath("//input[@name=\"SearchTerm\"]")\
                    .send_keys(sku)
                
                self.driver.find_element_by_xpath('//button[@name=\"simpleSearch\"]')\
                    .click()
                    
                print("Searching: ",sku)
                
                self.driver.find_element(By.LINK_TEXT, "Select All").click()
                
                print("Found: ",sku)
                 
                self.driver.find_element_by_xpath('//button[@id=\"deleteButton\"]')\
                    .click()
                
                print("Deleting: ", sku)
                
                self.driver.find_element_by_xpath('//button[@name=\"deletePrices\"]')\
                    .click()
                
                print("Deleted: ", sku)
                
                print(f"Remaining: {len(skus)} SKUs", skus)
                
                search = self.driver.find_element_by_xpath("//input[@name=\"SearchTerm\"]")
                search.clear()
            
        except:
               
                print("Error: Error occurred")
                print("Error: Remaining SKUs: ",skus)
                
                self.deletePrice(skus)
        


products = ["LW5CYWA","LW5CWRA","LW5BYKA"]
priceBook = '66198-CHF-SALE'
skus = ['113225555', 
'113225558', 
'113225559', 
]

names = [
    ['LW5CZWA', 'lululemon Align™ High-Rise Pant 26"'], 
['LW5CYBS', 'Here to There High-Rise 7/8 Pant'], 
['LM5A94S', 'ABC Commuter Pant 32"'], 
['LM3CC8S', 'Down To The Wire Long Sleeve Shirt'], 
['LW5CPPS', 'Here to There High-Rise 7/8 Pant'], 
['LW5DDRA', 'Invigorate High-Rise Tight 24"'], 
['LW5DE2A', 'lululemon Align™ Jogger'], 
['LW5DDZA', 'lululemon Align™ High-Rise Pant 26"'], 
['LW7BAJS', 'lululemon Align™ High-Rise Short 6"'], 
['LW9CNTS', 'Fast and Free Run Hat'], 
['LW5CR3A', 'lululemon Align™ Jogger'], 
['LW5CQFS', 'Invigorate High-Rise Tight 25"'], 
['LW8ABUT', 'Court Rival High-Rise Skirt 15"* Tall '], 
['LW5CTES', 'lululemon Align™ High-Rise Pant 28"'], 
['LW6BDRS', 'lululemon Align™ Jogger Crop'], 
['LW6BGIS', 'lululemon Align™ High-Rise Crop 21"'], 
['LU9A73S', 'The Reversible Mat 5mm'], 
['prod9200026', 'lululemon Align™ Jogger Crop 23"'], 
['LW2BIJS', 'Ebb to Street Bra *Light Support'], 
['LW7ARIT', 'Hotty Hot High-Rise Short 4"* Lined '], 
['LW7AY3S', 'Speed Up High-Rise Short 2.5"* Lined '], 
['LW5CF9A', 'Train Times High-Rise Tight 7/8* Asia Fit '], 
['LW5BJZS', 'Tightest Stuff High-Rise Tight 25"'], 
['LW1BSXS', 'lululemon Align™ Tank'], 
['prod9250073', 'Hotty Hot Short High-Rise Long 4"'], 
['LW8A78R', 'Pace Rival Skirt (Regular) 13"'], 

    ]

prim_cat = {'primary': ['masters']}
sub_cat = {'secondary': ['masters']}
      


my_bot = SFBot('hlau2@lululemon.com', pw)

""" Assign Single Primary Category """
# Tested: 
# my_bot.navProducts()
# my_bot.setCategories('prod1410121', 'women-tops-tanks')

""" Assign Multi Categories """
my_bot.getCategoryMapping('./csv/categories.csv')

# my_bot.navProducts()

""" Changing Multi Product Names """
# Tested:
# my_bot.navProducts()
# my_bot.changeAttribute(names)


""" Delete Multi Sale Prices """
# Tested: 
# my_bot.navPriceBook(priceBook)
# my_bot.deletePrice(skus)
