from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import csv 
# from secrets import pw
import pdb

class SFBot:
    def __init__(self, username, password, site):
        try:
            """ PERSONAL MAC """
            self.driver = webdriver.Chrome('/Users/harrisonlau/chromedriver')
        except:
            """ OFFICE WINDOWS """
            self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
        
        self.username = username

        self.password = password
        
        self.site = site
        
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
        if self.site == 'JP':
            idx = '1' 
        elif self.site == 'HK':
            idx = '5'

        script = 'arguments[0].selectedIndex = {}; arguments[0].onchange();'.format(idx)
        
        sites = self.driver.find_element_by_xpath('//select[@id="SelectedSiteID"]')
        self.driver.execute_script(script, sites)
        
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
    
    def setCategories(self, primary, secondary):
            
        while primary or secondary: 
            
            # POP keys with Set 
            # h = {1:'a', 2:'b'}
            # n = next(iter(h))
            # print(n)
            # h.pop(n)
            # print(h)

            try: 
                category = next(iter(primary))
                isPrimary = True
            except:
                category = next(iter(secondary))
                isPrimary = False
                
            try:
                products = ", ".join(list(primary[category]))
            except: 
                products = ", ".join(list(secondary[category]))
                
            print("Merchandising: ", category)
        
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
            
            try:
                search = self.driver.find_element_by_xpath("//input[@name=\"ext-comp-1009\"]")\
                    .send_keys(category)
            except:
                sleep(2)
                search = self.driver.find_element_by_xpath("//input[@name=\"ext-comp-1009\"]")\
                    .send_keys(category)
    
            try:
                self.driver.find_element(By.ID, "ext-comp-1009").send_keys(Keys.ENTER)
            
                print("Categorizing: ", products)
            
                self.driver.find_element(By.CSS_SELECTOR, ".x-grid3-row-checker").click()
            except:
                try:
                    search = self.driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/form/table[1]/tbody/tr[2]/td[2]/div/div/div/div/div[2]/div/div[1]/div/table/tbody/tr/td[2]/div/span/img[1]')
                    search.click()
                    
                    print("Categorizing: ", products)
                
                    self.driver.find_element(By.CSS_SELECTOR, ".x-grid3-row-checker").click()
                except:
                    continue 
            
            self.driver.find_element(By.NAME, "selectAction").click()
            
            if isPrimary:
                dropdown = self.driver.find_element_by_xpath('//select[@name="PrimaryCategoryUUID"]')
            
                options = dropdown.find_element_by_xpath("//option[contains(text(), 'lululemon')]")\
                    .click()
            
            self.driver.find_element_by_xpath('//button[@name="assignProductsAndReturn"]')\
                .click()
                
            print("Primary Categorized: %s > %s" % (products, category))
            
            try:
                primary.pop(category)
            except:
                secondary.pop(category)
                
            
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
                # Japanese (Japan) = 23
                # English (Hong Kong) = 7
                
                if self.site == 'JP':
                    idx = '23' 
                elif self.site == 'HK':
                    idx = '7'

                script = 'arguments[0].selectedIndex = {}; arguments[0].onchange();'.format(idx)
        
                self.driver.execute_script(script, lang)
        
                print("Language Selected")
                
                self.driver.find_element_by_link_text('Lock').click()
                # self.driver.find_element_by_xpath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/table[2]/tbody/tr/td[1]/table/tbody/tr[3]/td/table/tbody/tr/td[2]/p/a').click()
                
                print("Unlocked")
        
                name = self.driver.find_element_by_xpath('//*[@id="Metaf070c9f07840c78a8b2edc1902_Container"]/input')
                
                name.clear()
                
                name.send_keys(attribute)
        
                self.driver.find_element_by_xpath("//button[contains(text(), 'Apply')]").click()
                
                # Test to lock
                self.driver.find_element_by_link_text('Unlock').click()
                
                print("Applied")
                
                self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()
                
                done = names.pop(0)
                
                print(f"Remaining: {len(names)} names: ", names)
                
        except:
            
            print('Error: Error Occurred')
            
            print('Error: Remaining Pairs: ', names)
            
            self.changeAttribute(names)
            

    def getCategories(self, filename):

        """ LOGIC CHANGE NEEDED """
        # Need to change logic for if no search result

        pCats = {}
        sCats = {}

        with open (filename, newline = '', encoding='UTF-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader: 
                
                try:
                    """ PERSONAL MAC """
                    master = row['master']
                except:
                    """ OFFICE WINDOWS """
                    master = row['\ufeffmaster']
                
                primary = row['primaryCategory']
                secondary = [cat.strip() for cat in row['subCategories'].split(',')]

                if len(primary) < 1:
                    pass
                else:
                    if primary in pCats.keys():
                        pCats[primary].add(master)
                    else: 
                        pCats[primary] = set([master])
                
                for sec in secondary:
                    if len(sec) < 1:
                        continue
                    if sec in sCats.keys():
                        sCats[sec].add(master)
                    else:
                        sCats[sec] = set([master])
                    
        print("Primary Categories to merchandise: ",pCats)
        print("Sub Categories to merchandise: ",sCats)
        
        return [pCats, sCats]
        
    def getNames(self, filename):

        names = []

        with open (filename, newline = '', encoding='UTF-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader: 
                
                try:
                    """ PERSONAL MAC """
                    master = row['master']
                except:
                    """ OFFICE COMPUTER """
                    master = row['\ufeffmaster']
                
                name = row['name'].strip()
                
                pair = [master, name]
                
                names.append(pair)
                
        print("Changing names: ",names)
        return names
    
    def getSkus(self, filename):

        skus = []

        with open (filename, newline = '', encoding='UTF-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader: 
                
                try:
                    """ PERSONAL MAC """
                    sku = row['skus'].strip()
                except:
                    """ OFFICE COMPUTER """
                    sku = row['\ufeffskus'].strip()
                
                skus.append(sku)
                
        print("Changing skus: ",skus)
        return skus
    
    def getVariations(self, filename):

        variations = []

        with open (filename, newline = '', encoding='UTF-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader: 
                
                try:
                    """ PERSONAL MAC """
                    master = row['master']
                except:
                    """ OFFICE COMPUTER """
                    master = row['\ufeffmaster']
                
                styleNumber = row['styleNumber'].strip()
                
                colorID = row['colorID'].strip()
                
                pair = [master, styleNumber, colorID]
                
                variations.append(pair)
                
        print("Variations: ",variations)
        return variations

    def createVariants(self, variations):

        try:
            while variations: 
                # Takes first pair, when finished pop(0)
                pair = variations[0]
                print(pair)
                
                product = pair[0]
                styleNumber = pair[1]
                colorID = pair[2]
            
                search = self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]")
                search.send_keys(product)
                               
                self.driver.find_element_by_xpath('//button[@name=\"findIDList\"]')\
                    .click()
                
                self.driver.find_element_by_link_text(product)\
                    .click()
                
                self.driver.find_element_by_link_text('Variations').click()
                
                try: 
                    exist = self.driver.find_element_by_link_text(styleNumber)
                    if exist:
                        done = variations.pop(0)
                        self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()
                        continue
                        
        
                except:
                    pass
                
                try:
                    self.driver.find_element_by_link_text('Lock').click()
                    print("Unlocked")
                except:
                    pass
                
                self.driver.find_element_by_xpath("//input[@name=\"VariationGroupProductSKU\"]").send_keys(styleNumber)
                
                click = """button = document._getElementsByXPath('//button[@name="createVariationGroup"]');
                button[0].click();
                """
                
                
                try:
                    self.driver.find_element_by_xpath('//button[@name="confirmDisableSlicing"]')\
                        .click()
                    try:
                        self.driver.find_element_by_xpath('//button[@name="createVariationGroup"]')\
                            .click()
                    except:
                        self.driver.execute_script(click)
                    
                except:
                    self.driver.find_element_by_xpath('//button[@name="createVariationGroup"]')\
                        .click()
                            
                
                script = """table = document._getElementsByXPath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/form[1]/table[2]');
                let rows = table[0].rows
                let length = rows.length
                for (i = 0; i < length; i ++) {{
                        if (rows[i].innerText.include('{}')) {{
                                options = rows[i].getElementsByTagName('option')  
                                let k = options.length
                                select = rows[i].querySelector('select')        
                                for (j = 0; j < k; j++) {{
                                        if (options[j].value = '{}') {{        
                                                select.selectedIndex = 0;
                                                break;
                                            }}
                                        }}
                                }}
                        }}
                """.format(styleNumber, colorID)
                
                # print(script)
                
                # rows[2].innerText.include('LW5DDRA-034135')
                # options = rows[2].getElementsByTagName('option')        
                # select = rows[2].querySelector('select')        
                # options[0].value = '34135'        
                # select.selectedIndex = 0
                
                self.driver.execute_script(script)
                
                apply = """button = document._getElementsByXPath('//button[@name="applyVariationGroup"]');
                button[0].click();
                """
                
                try:
                    self.driver.find_element_by_xpath('//button[@name="applyVariationGroup"]')\
                        .click()
                except:
                    self.driver.execute_script(apply)
                
                
                self.driver.find_element_by_link_text('Unlock').click()
                        
                print("Applied")
                
                self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()
                
                done = variations.pop(0)
                
        except:
            
            print('Error: Error Occurred')
            
            print(f"Remaining: {len(variations)} variations: ", variations)
            
            raise

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
        




""" Creating instance of SFbot 🤖 """
site = input("Enter Site -").strip()
my_bot = SFBot('hlau2@lululemon.com', pw, site)


""" Assign Multi Categories ( ) """
"""Need to change logic for if no search result"""
# catFile = './csv/categories_' + site + '.csv'
# categories = my_bot.getCategories(catFile)
# primary = categories[0]
# secondary = categories[1]
# my_bot.navProducts()
# my_bot.setCategories(primary, secondary)

""" Changing Multi Product Names 😊 """
# names = my_bot.getNames('./csv/names.csv')
# my_bot.navProducts()
# my_bot.changeAttribute(names)


""" Delete Multi Sale Prices 😊 """
# priceBook = input("Enter PriceBook -").strip()
# skus = my_bot.getSkus('./csv/skus.csv')
# my_bot.navPriceBook(priceBook)
# my_bot.deletePrice(skus)

""" Create Variant Groups 😊 """ 
variations = my_bot.getVariations('./csv/variations.csv')
my_bot.navProducts()
my_bot.createVariants(variations)












""" DATA STRUCTURES """

# priceBook = '66198-CHF-SALE'

# skus = ['113225555', 
# '113225558', 
# '113225559', 
# ] 

# names = [
#     ['LW5CZWA', 'lululemon Align™ High-Rise Pant 26"'], ['LW5CYBS', 'Here to There High-Rise 7/8 Pant'], 
#     ]

# prim_cat = {'primary': {'masters'}}
# sub_cat = {'secondary': {'masters'}}