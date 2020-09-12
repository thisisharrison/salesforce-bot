from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import csv 
from bs4 import BeautifulSoup
import requests
from secrets import pw
import pdb

class SFBot:
    def __init__(self, username, password, site):
        # Locate Chrome Driver
        try:
            """ PERSONAL MAC """
            self.driver = webdriver.Chrome('/Users/harrisonlau/chromedriver')
        except:
            """ OFFICE WINDOWS """
            self.driver = webdriver.Chrome()
        # Set implicit wait time
        self.driver.implicitly_wait(5)
        
        # Credentials
        self.username = username
        self.password = password
        self.site = site
        
        # Go to login site
        self.driver.get("https://staging-eu01-lululemon.demandware.net/on/demandware.store/Sites-Site/default/ViewLogin-StartAM")
        self.driver.find_element_by_xpath("//button[contains(text(), 'Log In')]")\
            .click()
        self.login()

    def login(self):

        try:
            # Enter username
            self.driver.find_element_by_xpath("//input[@name=\"callback_0\"]")\
                .send_keys(self.username)
            self.driver.find_element_by_xpath('//input[@type="submit"]')\
                .click()
            # Enter password
            self.driver.find_element_by_xpath("//input[@name=\"callback_1\"]")\
                .send_keys(self.password)
            self.driver.find_element_by_xpath('//input[@type="submit"]')\
                .click()
        
        except Exception as error:
            print(error)
            print("Retry logging in...")
            self.login()

        """ Select Site """
        if self.site == 'JP':
            idx = '1'
        elif self.site == 'UK':
            idx = '5'
        elif self.site == 'HK':
            idx = '5'
        elif self.site == 'AU':
            idx = '7'

        script = 'arguments[0].selectedIndex = {}; arguments[0].onchange();'.format(idx)
        
        sites = self.driver.find_element_by_xpath('//select[@id="SelectedSiteID"]')
        self.driver.execute_script(script, sites)
        
        print("Logged in as: ", self.username)
        
        sleep(3)

    """ Navigate to Product Page """
    def navProducts(self):
        
        try: 
            self.driver.find_element(By.CSS_SELECTOR, ".menu .merchant-tools-link > .menu-overview-link-icon").click()
        
            sleep(3)
                  
            self.driver.find_element_by_link_text('Products').click()
        
        except Exception as error:
            print(error)
            print("Alternative Navigation")
            
            self.driver.find_element_by_link_text('Merchant Tools')\
                .click()
            
            self.driver.find_element_by_link_text('Products and Catalogs')\
                .click()
            
            self.driver.find_element_by_link_text('Products')\
                .click()
            
        sleep(3)
        
        self.driver.find_element_by_link_text('By ID')\
            .click()
          
        print("Product Page")
    
    def copyProductStatus(self, products):
            
        # b = a[0:len(a)]
        # del a[0:len(a)]

        while products:
            if len(products) > 1000:
                print(len(products))
                
                search = products[0:1000]
                print(len(search))
                search = ",".join(search)
                
                del products[0:1000]
                print("====")
                print(len(products))
            else:
                search = ", ".join(products)
                del products[0:len(products)]
                
            search_bar = self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]")
                
            search_bar.send_keys(search)
        
            print("Searching -{}".format(len(search)))
                
            self.driver.find_element_by_xpath('//button[@name=\"findIDList\"]')\
                    .click()
                    
            all_button = """
                    button = document._getElementsByXPath('//button[@name="PageSize"]');
                    button[button.length -1].click()
                """
            try:
                self.driver.execute_script(all_button)                
            except: 
                pass
            
            table = self.driver.find_element_by_xpath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/form/table/tbody/tr/td/table[1]')
            content = table.get_attribute('outerHTML')
            with open("searchresult.txt", "a", encoding='utf-8') as file:
                file.write(content)
            
            self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]").clear()
            
    """ Search for Products in Products Tool """
    def searchProducts(self, products):
        self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]")\
                .send_keys(products)
            
        print("Searching: ", products)
        
        self.driver.find_element_by_xpath('//button[@name=\"findIDList\"]')\
            .click()

    """ Get Primary and SubCategories Assignment from CSV to pass to #setCategories """
    def getCategories(self, filename):
        
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
                
                # not primary for this product
                if len(primary) < 1:
                    pass
                else:
                    # add to primary list
                    if primary in pCats.keys():
                        pCats[primary].add(master)
                    else: 
                        # remove duplicate masters 
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

    """ Assign Primary and Subcategories to Products """
    def setCategories(self, primary, secondary):
            
        while primary or secondary: 

            try: 
                category = next(iter(primary))
                isPrimary = True
                job = "Primary Categorized"
            except:
                category = next(iter(secondary))
                isPrimary = False
                job = "Secondary Categorized"
                
            try:
                products = ", ".join(list(primary[category]))
            except: 
                products = ", ".join(list(secondary[category]))
                
            print("Merchandising: ", category)

            self.searchProducts(products)

            # self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]")\
            #     .send_keys(products)
            
            # print("Searching: ", products)
            
            # self.driver.find_element_by_xpath('//button[@name=\"findIDList\"]')\
            #     .click()
            
            try:
                self.driver.find_element_by_xpath('//button[@name=\"EditAll\"]')\
                    .click()
            except:
                edit_all = """
                    button = document._getElementsByXPath('//button[@name=\"EditAll\"]')
                    button[0].click()
                """
                self.driver.execute_script(edit_all)
                
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
                
            print("%s: %s > %s" % (job, products, category))
            
            try:
                primary.pop(category)
            except:
                secondary.pop(category)
                
    """ Change products' names """        
    def setNames(self, names):
        
        try: 
            while names:
                
                # Takes first pair, when finished pop(0)
                pair = names[0]
                print(pair)
                
                product = pair[0]
                attribute = pair[1]
            
                self.searchProducts(product)
                
                # search = self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]")
                # search.send_keys(product)
                               
                # self.driver.find_element_by_xpath('//button[@name=\"findIDList\"]')\
                #     .click()
                
                self.driver.find_element_by_link_text(product)\
                    .click()
                
                # Select language
                lang = self.driver.find_element_by_xpath('//select[@name="LocaleID"]')
                
                """ SELECT LANGUAGE """
                if self.site == 'JP':
                    idx = '23' 
                elif self.site == 'HK':
                    idx = '7'

                script = 'arguments[0].selectedIndex = {}; arguments[0].onchange();'.format(idx)
        
                self.driver.execute_script(script, lang)
        
                print("Language Selected")
                
                try:
                    self.driver.find_element_by_link_text('Lock').click()
                except:
                    pass
                print("Unlocked")
        
                name = self.driver.find_element_by_xpath('//*[@id="Metaf070c9f07840c78a8b2edc1902_Container"]/input')
                
                name.clear()
                
                name.send_keys(attribute)
        
                self.driver.find_element_by_xpath("//button[contains(text(), 'Apply')]").click()
                
                self.driver.find_element_by_link_text('Unlock').click()
                
                print("Applied")
                
                self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()
                
                done = names.pop(0)
                
                print(f"Remaining: {len(names)} names: ", names)
                
        except Exception as error:
            
            print(error)
            
            print('Error: Remaining Pairs: ', names)
            
            self.setNames(names)

    """ Get Names for #setNames to change Products' Names """    
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
    
    """ Get SKUs from CSV """
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
    
    """ Get Variation Mapping for Product Variation Groups """
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
                
        except Exception as error:
            print(error)
            print(f"Remaining: {len(variations)} variations: ", variations)
            try: 
                self.navProducts()
                self.createVariants(variations)
            except Exception as error: 
                print(error)
                raise

    """ Navigate to Pricebook Page """
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

        print("Price Book Page")
        
    """ Delete Pricing from Price Book """
    def deletePrice(self, skus):
                    
        search = self.driver.find_element_by_xpath("//input[@name=\"SearchTerm\"]")
        search.clear()
        
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
            
        except Exception as error:
            print(error)
            print("Error: Remaining SKUs: ",skus)
            self.deletePrice(skus)
    
    """ Get Front Facing Colors from CSV """
    def getFrontColor(self, filename):
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
                
                colors = [color.strip() for color in row['colors'].split(",")]
                
                pair = [master, colors]
                
                variations.append(pair)
                
        print("Variations: ",variations)
        return variations
    
    """ Update Front Color """
    def updateFrontColor(self, variations):
        try:
            while variations: 
                # Takes first pair, when finished pop(0)
                pair = variations[0]
                print(pair)
                
                product = pair[0]
                colors = [color.lower() for color in pair[1]]
                first_color = colors[0]
                
                print("Product -", product)
                print("Colors -", colors)
                print("First Color -", first_color)
                
                search = self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]")
                search.send_keys(product)
                               
                self.driver.find_element_by_xpath('//button[@name=\"findIDList\"]')\
                    .click()
                
                self.driver.find_element_by_link_text(product)\
                    .click()
                
                self.driver.find_element_by_link_text('Variations').click()
                
                self.driver.find_element_by_link_text('color ⁄ color').click()
                
                try:
                    self.driver.find_element_by_link_text('Lock').click()
                except: 
                    pass
                
                all_button = """
                    button = document._getElementsByXPath('//button[@name="PageSize"]');
                    button[1].click()
                """
                try:
                    self.driver.execute_script(all_button)                
                except: 
                    pass
                
                color_script = """
                            table = document._getElementsByXPath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/form/table[4]');
                            rows = table[0];
                            inputs = rows.querySelectorAll('input');
                            
                            length = inputs.length
                            colors = {}
                            
                            for (let i = 0; i < length; i++) {{
                                name = inputs[i].value.toLowerCase();    
                                if (colors.include(name)) {{
                                        inputs[i-2].click();
                                }}
                            }}
                            button = rows.querySelector('input[name="moveTop"]');
                            button.click();
                            

                                    
                """.format(colors)
                self.driver.execute_script(color_script)             

                # confirm_script = """
                #             table = document._getElementsByXPath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/form/table[4]');
                #             rows = table[0];
                #             inputs = rows.querySelectorAll('input');
                            
                #             length = inputs.length
                #             colors = {}
                #             first = colors[0]
                #             table_first = inputs[4].value.toLowerCase()
                            
                #             if (first != table_first) {{
                #                 for (let i = 0; i < length; i++) {{
                #                     name = inputs[i].value.toLowerCase();    
                #                     if (first === name) {{
                #                             inputs[i-2].click();
                #                     }}
                #                     break;
                #                 }}
                #                 button = rows.querySelector('input[name="moveTop"]');
                #                 button.click();                            
                #             }}
                # """.format(colors)
                # self.driver.execute_script(confirm_script)
                               
                self.driver.find_element_by_link_text('Unlock').click()
                self.driver.find_element_by_link_text('Products').click()
                
                done = variations.pop(0)
                print("Complete pair -", pair)
        except Exception as error:
            print(error)
            raise
    
    """ Get Styles of Missing Images """
    def getMissingImage(self, filename):
        pass
    
    """ Add Missing Images for Styles"""
    def addMissingImage(self, s, pairs):
        while pairs:    
            pair = pairs[0]

            product = pair[0]
            color = pair[1]
            style_color = pair[2]
            
            color = color.lower()
            style_color = style_color.replace("-","_")
            
            domain = "https://images.lululemon.com/is/image/lululemon/"
            avail_img = [style_color + '_' + str(i) for i in range(10) if s.get(domain + style_color + '_' + str(i)).status_code == 200]
            print("Available images -",avail_img)
            
            self.searchProducts(product)
            # search = self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]")
            # search.send_keys(product)
                        
            # self.driver.find_element_by_xpath('//button[@name=\"findIDList\"]')\
            #     .click()
            
            self.driver.find_element_by_link_text(product)\
                .click()
            
            try:
                self.driver.find_element_by_link_text('Lock').click()
            except:
                pass
            print("Unlocked")
            
            # Edit Image
            try:
                self.driver.find_element(By.ID, "imageSpecificationButton").click()
            except:
                button = """
                    document.querySelector('#imageSpecificationButton').click()
                """
                self.driver.execute_script(button)
            # Product Master
            try:
                # self.driver.find_element(By.ID, "extdd-27").click()
                self.driver.find_element_by_xpath("//span[contains(text(),'product master')]").click()
            except:
                productmaster = """
                    document.querySelector('#extdd-27').click()
                """
                self.driver.execute_script(productmaster)
            
            if self.selectColor(color):
                pass
            # Color is hidden and need to add color back
            else:
                self.driver.find_element_by_id('ext-gen98').click()
                sleep(3)
                table = self.driver.find_element_by_xpath('//*[@id="ext-gen286"]/div/li/ul')
                li = table.find_elements_by_class_name('x-tree-node')
                
                for i in range(len(li)):
                    if color in li[i].get_attribute("innerHTML").lower():
                        li[i].find_element_by_class_name('x-tree-node-cb').click()
                        self.driver.find_element_by_id('ext-gen230').click()
                        self.selectColor(color)

                
            # Use to check if first image already exists to avoid adding first image again
            checkFirst = True
            
            while avail_img:
                # Gets the rows (hi-res, large, medium, small) and last idx is fill in style color 
                img = avail_img[0]
                script = """
                body = document._getElementsByXPath('//*[@id="ext-gen122"]')
                body = body[0]
                node_list = body.querySelectorAll('div.x-tree-node-el.x-tree-node-leaf.x-unselectable');
                    
                n = Array.from(node_list)
                map = n.map(x => x.querySelector('table'))
                rows = map.filter(x => x != null)
                
                return rows
                """
                rows = self.driver.execute_script(script)
                
                table = [x.get_attribute('innerHTML') for x in rows]
                content = " ".join(table)
                soup = BeautifulSoup(content, "html.parser")
                anchors = soup.find_all(class_="img-mgr-image-node img-mgr-image-node-border x-tree-node-icon x-tree-node-inline-icon")
                ids = [x.get('id') for x in anchors]
                
                if checkFirst:
                    first_box = self.driver.find_element_by_id(ids[0])
                    detail_path = self.driver.find_element_by_id('detail_path')
                
                    first_box.click()

                    if style_color + '_1' in detail_path.get_attribute('value'):
                        done = avail_img.pop(0)
                        checkFirst = False
                        continue
                
                # Need to deal with missing swatch for checkFirst True (0 images) and for those it is not len(id) - 3

                for i in range(len(ids)-3):
                    el = self.driver.find_element_by_id(ids[i]).get_attribute('outerHTML')
                    if style_color in el:
                        continue
                    else:
                        self.driver.find_element_by_id(ids[i]).click()
                        self.driver.find_element_by_id('detail_path').send_keys(img)
                
                done = avail_img.pop(0)
                    
            try:
                save = self.driver.find_elements_by_xpath('//*[@id="ext-gen79"]')
                save.click()
            except:
                self.driver.find_element_by_xpath("//button[contains(text(), 'Save')]")\
                    .click()
            
            done = pairs.pop(0)

            self.driver.find_element_by_link_text('Unlock').click()
            self.driver.find_element_by_link_text('Products').click()
                
            print("Complete pair -", pair)
        
    """ Select Color to Add Images to """
    def selectColor(self, color):
        try:
            capitalize_color = " ".join([el.capitalize() for el in color.split(" ")])
            colorpath = "//span[contains(text(),'{}')]".format(capitalize_color)
            self.driver.find_element_by_xpath(colorpath).click()
            return True
        except:
            try:
                colorpath = "//span[contains(text(),'{}')]".format(color)
                self.driver.find_element_by_xpath(colorpath).click()
                return True
            except:
                select_color = """
                nodes = document.querySelectorAll('.x-tree-node');
                nodes_list = Array.from(nodes);
                nodes_list.shift();
                length = nodes_list.length;
                found = false
                for (let i = 1; i < length; i++) {{
                        node = nodes_list[i].innerText.toLowerCase();
                        if (node.includes('{}')) {{
                                nodes_list[i].querySelector('a').click();
                                found = true
                        }}
                        break;
                }}
                if (found) {{
                    return True
                }} else {{
                    return ''
                }}
                """.format(color)
                found = self.driver.execute_script(select_color)
                return bool(found)
        return False

##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### 

    def hreflang(self):
        
        try: 
            
            self.driver.find_element(By.CSS_SELECTOR, ".menu .merchant-tools-link > .menu-overview-link-icon").click()
            
            sleep(3)
            
            self.driver.find_element(By.LINK_TEXT, "Catalogs").click()
        
        except: 
        
            self.driver.find_element_by_link_text('Merchant Tools')\
                .click()
            
            self.driver.find_element_by_link_text('Products and Catalogs')\
                .click()
            
            self.driver.find_element_by_link_text('Catalogs')\
                .click()
            
            print("Alternative Navigation")
        
        if self.site == 'JP':
            nav = 'lululemon-jp-navigation' 
        elif self.site == 'UK':
            nav = 'lululemon-emea-navigation'
        elif self.site == 'HK':
            nav = 'lululemon-hk-navigation'
        elif self.site == 'AU':
            nav = 'lululemon-ausnz-navigation'
        
        self.driver.find_element_by_link_text(nav)\
                .click()
        
        self.seo_filename = './csv/logs/' + self.site + "_BM_categories(Request).csv"
        
        with open(self.seo_filename, "w", encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID','Hreflangtag', 'Edit link'])
           
        try:
            self.driver.find_element_by_xpath('//button[@name=\"CategoryPageSize\"]')\
                .click()
        except:
            raise
            pass
                
        edit_script = """
                table = document._getElementsByXPath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td/form[2]/table/tbody/tr/td/table[1]');
                links = table[0].querySelectorAll('.action_link');
                array = Array.prototype.slice.call(links);
                return array.map(link=>link.href);
        """
        
        edit_links = self.driver.execute_script(edit_script)
        
               
        print("Edit Links -",len(edit_links))
        
        cdp_script = """
                table = document._getElementsByXPath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td/form[2]/table/tbody/tr/td/table[1]');
                links = table[0].querySelectorAll('.table_detail_link');
                array = Array.prototype.slice.call(links);
                return array.map(link=>link.href);
        """
        cdp_links = self.driver.execute_script(cdp_script)
        
        cdp_links = list(set(cdp_links))
        
        print("CDP Links -",len(cdp_links))
              
        self.attr_toCSV(edit_links)
        
        try:
            self.driver.find_element_by_link_text(nav)\
                .click()
        except:
            self.driver.find_element_by_link_text('Lululemon EU_EN Navigation')\
                .click()
        
        self.recursion_catalog(cdp_links)
        
        
            
    def catalog_crawl(self, link):
        self.driver.get(link)
        try:
            self.driver.find_element_by_xpath('//button[@name=\"CategoryPageSize\"]')\
                .click()
        except:
            pass
                      
        cdp_button = """
                table = document._getElementsByXPath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td/form[2]/table/tbody/tr/td/table[1]');
                links = table[0].querySelectorAll('.table_detail_link');
                array = Array.prototype.slice.call(links);
                return array.map(link=>link.href);
        """
        cdp_links = self.driver.execute_script(cdp_button)
        
        cdp_links = list(set(cdp_links))
        
        self.category_attr_crawl(link)       
               
        print("CDP Links -",len(cdp_links))
        return cdp_links or []

    def category_attr_crawl(self, link):
        edit_script = """
                table = document._getElementsByXPath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td/form[2]/table/tbody/tr/td/table[1]');
                links = table[0].querySelectorAll('.action_link');
                array = Array.prototype.slice.call(links);
                return array.map(link=>link.href);
        """
        
        edit_links = self.driver.execute_script(edit_script)
        
        print("Edit Links -",len(edit_links))
        
        self.attr_toCSV(edit_links)
        self.driver.get(link)
        
    def attr_toCSV(self, edit_links):
        with open(self.seo_filename, "a", encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
                        
            for edit in edit_links: 
                
                self.driver.get(edit)
                
                category_id = self.driver.find_element_by_xpath("//input[@name=\"RegFormAddCategory_Id\"]").get_attribute('value')
                
                self.driver.find_element_by_link_text('Category Attributes').click()
    
                href_lang_tag = self.driver.find_element_by_xpath('//*[@id="Meta12caa1c79d61919817dda9fecd"]').get_attribute('value')
                
                print(category_id)
                print(href_lang_tag)
                
                copy = [category_id, href_lang_tag, edit]
                
                writer.writerow(copy)
            f.close()
        
        

    def recursion_catalog(self, cdp_links):
        # We finished the list of CDPs
        if not cdp_links:
            return [] 
        # Bot did not find any more CDPs in this path
        try:
            self.driver.find_element_by_xpath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td/form[2]/table/tbody/tr/td/table[1]')
        except:
            return []
                    
        link = cdp_links[0]
        
        print(link)
        
        new_links = self.catalog_crawl(link)
        
        cdp_links += new_links
        
        done = cdp_links.pop(0)
       
        total = [link] + new_links + self.recursion_catalog(cdp_links)
        
        # Recursion error: Not returning but able to save all category IDs
        print(total)
        
    def updateHref(self, filename):
        
        with open (filename, newline = '', encoding='UTF-8') as csvfile:
            
            reader = csv.DictReader(csvfile)
            
            for row in reader: 
                            
                edit_link = row['edit_link'].strip()
                
                new_langtag = row['new langtag'].strip()
                
                self.driver.get(edit_link)
                
                self.driver.find_element_by_link_text('Category Attributes').click()
    
                textarea = self.driver.find_element_by_xpath('//*[@id="Meta12caa1c79d61919817dda9fecd"]')
                
                textarea.clear()
                
                textarea.send_keys(new_langtag)
                                
                apply_script = """
                    button = document._getElementsByXPath('//*[@id="bm_content_column"]//button')[2];
                    button.click()
                """
                
                self.driver.execute_script(apply_script)
          
        return True
    
        
""" Clean up Hrefs in CSV """    
def getPairs():
    with open ("./csv/seo/old_to_new_hrefs.csv", newline = '', encoding='UTF-8') as csvfile:
        reader = csv.DictReader(csvfile)
        pairs = []
        
        for row in reader: 
            
            try:
                """ PERSONAL MAC """
                old = row['old'].strip()
            except:
                """ OFFICE COMPUTER """
                old = row['\ufeffold'].strip()
            
            new = row['new'].strip()
            
            pair = [old, new]
            
            pairs.append(pair) 
        print(pairs)
        return pairs

def updateHrefCSV():
    with open("./csv/seo/category_edit_links.csv", newline = '', encoding='UTF-8') as csvfile:
        reader = csv.DictReader(csvfile)
        pairs = getPairs()
        
        with open("./csv/seo/new_href_langtag.csv", "w", encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "old langtag", "new langtag", "edit_link"])
        
            for row in reader:
                try:
                    ID = row['\ufeffID'].strip()
                except:
                    ID = row['ID'].strip()
                
                old = row['Hreflangtag'].strip()
                
                edit_link = row['Edit link'].strip()
                
                new = old
                
                for pair in pairs:
                    if pair[0] in new: 
                        new = new.replace(pair[0], pair[1])
                        print("{} => {}".format(pair[0],pair[1]))
                 
                writer.writerow([ID, old, new, edit_link])    

##### MAIN SCRIPTS ##### ##### MAIN SCRIPTS ##### ##### MAIN SCRIPTS ##### ##### MAIN SCRIPTS ##### ##### MAIN SCRIPTS ##### ##### MAIN SCRIPTS ##### ##### MAIN SCRIPTS ##### 



""" Creating instance of SFbot 🤖 """
site = input("Enter Site -").strip()
my_bot = SFBot('hlau2@lululemon.com', pw, site)


""" Assign Multi Categories 😊 """
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
# my_bot.setNames(names)


""" Delete Multi Sale Prices 😊 """
# priceBook = input("Enter PriceBook -").strip()
# skus = my_bot.getSkus('./csv/skus.csv')
# my_bot.navPriceBook(priceBook)
# my_bot.deletePrice(skus)


""" Create Variant Groups 😊 """ 
# variations = my_bot.getVariations('./csv/variations.csv')
# my_bot.navProducts()
# my_bot.createVariants(variations)


""" Recursive HRefLang Crawl 😊 """
# my_bot.hreflang()


""" HRefland Update 😊 """
# updateHrefCSV()
# my_bot.updateHref('./csv/seo/new_href_langtag.csv')


""" Return Search Results in CSV 😢 """
# my_bot.navProducts()
# products = [x.strip() for x in input("Enter Products -").splitlines()]
# my_bot.copyProductStatus(products)


""" Change front color 😢 """
"""Missing ability to use the first color in list as front"""
# variations = my_bot.getFrontColor('./csv/colors.csv')
# my_bot.navProducts()
# my_bot.updateFrontColor(variations)


""" Add missing images 😢 """
my_bot.navProducts()
s = requests.Session()
# filename = ''
# pairs = my_bot.getMissingImage(filename)

product = 'prod9850150'
color = "Heathered Mod Faint Coral"
style_color = 'LW3BZVS-037724'
pairs = [[product, color, style_color]]

my_bot.addMissingImage(s, pairs)



""" Passing Selenium Cookie to Request 😢 """
# s = requests.Session()
# cookies = my_bot.driver.get_cookies()
# print(cookies)
# for c in cookies:
#     s.cookies.set(c['name'], c['value'])
# url = "https://staging-eu01-lululemon.demandware.net/on/demandware.store/Sites-Site/default/ViewChannelCatalog_52-Dispatch?csrf_token=0JOLo-i209l4giKiJy_Ay9fbY0Oxfm1InckMa8PPYEpCT_W7dcLAmdviGlhdGwgJ6Y7gIsbsa6AJ9zvBG9nkKpzX_AhmH8HwV03aoqdpzS-kcLwNj70soHFcluPo9cC3KVvNuBBCvej1nOJUGWpiPOtM-8ULd4QGMDtRsHQ_wdpCkOoh7oM="
# resp = s.get(url)
# print(resp.status_code)
# soup = BeautifulSoup(resp.text, "html.parser")

# pdb.set_trace()


""" Passing Selenium Cookie to urllib 😢 """

""" Controller for the Bot 🤖 """
# running = True

# while running:
#     site = input("Enter Site -").strip()
#     my_bot = SFBot('hlau2@lululemon.com', pw, site)    
#     action = input("What do you want? -")
#     cases = {
#         'q': my_bot.driver.quit()
#     }
#     cases[action]
#     if action == "q":
#         running = False


