from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import csv 
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
import requests
import os
# from secrets import pw
import pdb
from styleNumberRefinement import styleNumberRefinement, skuAttributeRefinement

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
        
        # User's directory
        self.dir = os.path.dirname(os.path.realpath(__file__))
        
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
            idx = '8'
        elif self.site == 'HK':
            idx = '5'
        elif self.site == 'AU':
            idx = '7'
        elif self.site == 'DE':
            idx = '2'
        
        sleep(3)
        
        script = 'arguments[0].selectedIndex = {}; arguments[0].onchange();'.format(idx)
        
        sites = self.driver.find_element_by_xpath('//select[@id="SelectedSiteID"]')
        self.driver.execute_script(script, sites)
        
        print("Logged in as: ", self.username)
        
        if self.site == 'DE':
            self.site = 'UK'
        
        sleep(3)

    """ Navigate to Product Page """
    def navProducts(self):
        
        self.driver.get("https://staging-eu01-lululemon.demandware.net/on/demandware.store/Sites-Site/default/ViewProductList_52-List?SelectedMenuItem=prod-cat&CurrentMenuItemId=prod-cat&CatalogItemType=Product")
        
        try:
            self.driver.find_element_by_link_text('By ID')\
            .click()
        except: 
            pass
          
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
            
            filename = "./csv/" + self.site + "_searchResult.txt"
            
            with open(filename, "a", encoding='utf-8') as file:
                file.write(content)
            
            self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]").clear()
            
    """ Search for Products in Products Tool """
    def searchProducts(self, products):
            
        self.driver.find_element_by_xpath("//textarea[@name=\"WFSimpleSearch_IDList\"]")\
                .send_keys(products)
            
        print("Searching: ", products)
        
        try:
            self.driver.find_element_by_xpath('//button[@name=\"findIDList\"]').click()
        except Exception as error: 
            self.helpMeHuman(error)

    def editAll_ProductTool(self):
        try:
            self.driver.find_element_by_xpath('//button[@name=\"EditAll\"]')\
                .click()
        except:
            edit_all = """
                button = document._getElementsByXPath('//button[@name=\"EditAll\"]')
                button[0].click()
            """
            self.driver.execute_script(edit_all)
        
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
            
            # try:
            #     self.driver.find_element_by_xpath('//button[@name=\"EditAll\"]')\
            #         .click()
            # except:
            #     edit_all = """
            #         button = document._getElementsByXPath('//button[@name=\"EditAll\"]')
            #         button[0].click()
            #     """
            #     self.driver.execute_script(edit_all)
            
            self.editAll_ProductTool()
                
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
    
            print("Categorizing: ", products)
            
            try:
                self.driver.find_element(By.ID, "ext-comp-1009").send_keys(Keys.ENTER)
            
                self.driver.find_element(By.CSS_SELECTOR, ".x-grid3-row-checker").click()
            except:
                try:
                    search = self.driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/form/table[1]/tbody/tr[2]/td[2]/div/div/div/div/div[2]/div/div[1]/div/table/tbody/tr/td[2]/div/span/img[1]')
                    search.click()
                
                    self.driver.find_element(By.CSS_SELECTOR, ".x-grid3-row-checker").click()
                except:
                    message = "Category ID not found. Search ID and select the checkbox then enter 'y'."
                    self.helpMeHuman(message)
 
            
                        
            try:
                self.driver.find_element(By.NAME, "selectAction").click()
            except:
                self.driver.find_element_by_xpath('//button[@name="selectAction"]').click()
                try:
                    selectAction = """document._getElementsByXPath('//button[@name="selectAction"]')[0].click();
                    """
                    self.driver.execute_script(selectAction)
                except:
                    message = "This is embarrassing. Press Next for me please!"
                    self.helpMeHuman(message)
            
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

    def helpMeHuman(self, message):
        print("Hey %s user! I'm in a pickle here..." % (self.site))
        print("Can you help me?")
        print("Message: " + message)
        stuck = True
        
        while stuck:
            user = input("Are we ready? > ")
            if user != 'y':
                continue
            else:
                stuck = False
                break            
        
        return
        
        
    def selectLanguage(self, option = None):
        if not option:
            option = self.site
        
        # Select language
        try:
            lang = self.driver.find_element_by_xpath('//select[@name="LocaleID"]')
        except:
            lang = self.driver.find_element_by_xpath('//select[@name="LocaleId"]')
            
        """ SELECT LANGUAGE """
        indices = {
            'JP': '23',
            'HK': '7',
            'UK': '12',
            'DE': '19',
            'DE_DE': '20',
            'DE_LX': '21',
            'DE_SW': '22',
            }
           
        script = 'arguments[0].selectedIndex = {}; arguments[0].onchange();'.format(indices[option])
        
        self.driver.execute_script(script, lang)

        print("Language Selected")
        
    def categoryPosition(self):
        url = input("Enter catgeory url > ")
        # url ="https://staging-eu01-lululemon.demandware.net/on/demandware.store/Sites-Site/default/ViewChannelCatalog_52-Browse?CatalogCategoryID=4f591255d02df8235d17dd5c05&CatalogID=lululemon-hk-navigation&BackTo=CategoryList&csrf_token=KvH9QoADsj1Yom6iDpVmbcI1KurMv4kQlu5sqXwqD8enUoyReiZELY3fVZUUTqcfjlnUNl-A5854EXZUxU81do-Loky15Cx1b7XI3yMHTqvTyIBUuZI9GAotaoVZWhZnM8bfTMQujWeGPnj68vZIoJDFHryYF_Z-dxWBg4COERNCfZD-5nc="
        
        mapping = self.getNewCategoryPosition()
        
        self.driver.get(url)
        
        # pdb.set_trace()
        
        # Expand to view all products
        try:
            self.expandCategoryPosition()
        except:
            pass
        
        self.categoryPositionClear()
        # self.updatePositionsButton()        
        
        # pdb.set_trace()
        # update new positions
        self.categoryPositionUpdate(mapping)

        self.driver.find_element_by_xpath("//body").send_keys(Keys.END)
        

        # self.helpMeHuman("Click Apply")
        self.updatePositionsButton()
        
        
        
    def updatePositionsButton(self):
        button = """document._getElementsByXPath("//button[@id='updatePositions']")[0].click()"""
        self.driver.execute_script(button)

    def expandCategoryPosition(self):
        self.driver.find_element_by_xpath("//body").send_keys(Keys.END)
        sleep(2)
        self.driver.find_element_by_xpath('//button[text()="All"]').click()
        
        
    def getNewCategoryPosition(self):
        with open('./csv/changeCatPos.csv', encoding = 'utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            mapping = {}
            
            for row in reader:
                ID = row['ID']
                position = row['position']
                mapping[position] = ID
            
            return mapping
    
    def categoryPositionClear(self):
        table = self.driver.find_element_by_xpath('//input[@name="ProductFormSubmitted"]/following-sibling::table')
        input_fields = table.find_elements_by_xpath('//*[contains(@name, "NewPosition")]')
        
        for i in input_fields:
            if i.get_attribute("value"):
                print(i.get_attribute("value"))
                try:
                    i.click()
                    i.clear()
                    self.driver.execute_script("arguments[0].removeAttribute('value')", i)
                except:
                    self.driver.execute_script("arguments[0].scrollIntoView();", i)
                    self.driver.execute_script("window.scrollBy(0,-100)")
                    i.click()
                    i.clear()
                    self.driver.execute_script("arguments[0].removeAttribute('value')", i)
            else:
                continue
        
        return
        
    def categoryPositionUpdate(self, mapping):
    
        for k, v in mapping.items():
        
            print("{} => {}".format(v, k))
                            
            # if (inputs)
            
            script = """inputs = document._getElementsByXPath('//*[contains(text(),"{}")]')[0].parentNode.parentNode.getElementsByTagName('input');
            
            if (inputs) {{
            for (let i = 0; i < inputs.length; i++) {{
                    if (inputs[i].getAttribute('name').includes('NewPosition_')) {{
                            inputs[i].click();
                            inputs[i].value = {};
                            }}
                    else
                        continue;
                    }}
            }}
            """.format(v,k)
            
            self.driver.execute_script(script)
        
        
        return
            
    
        
                
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
                
                # # Select language
                # lang = self.driver.find_element_by_xpath('//select[@name="LocaleID"]')
                
                # """ SELECT LANGUAGE """
                # if self.site == 'JP':
                #     idx = '23' 
                # elif self.site == 'HK':
                #     idx = '7'

                # script = 'arguments[0].selectedIndex = {}; arguments[0].onchange();'.format(idx)
        
                # self.driver.execute_script(script, lang)
        
                # print("Language Selected")
                    
                self.selectLanguage()
                
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

    def setProductAttributes(self, products):
        
        try: 
            while products:
                
                # Takes first pair, when finished pop(0)
                pair = products[0]
                print(pair)
                
                product = pair[0]
                attrs = pair[1]
            
                self.searchProducts(product)
                self.driver.find_element_by_link_text(product).click()                    
                self.selectLanguage()
                
                try:
                    self.driver.find_element_by_link_text('Lock').click()
                except:
                    pass
                print("Unlocked")
                
                # pdb.set_trace()
                
                if attrs['name']:
                    self.changeName(attrs['name'])
                if attrs['whyWeMadeThis']:
                    self.changeWWMT(attrs['whyWeMadeThis'])
                if attrs['careDescription']:
                    self.changeCareDescription(attrs['careDescription'])
                if attrs['features']:
                    self.changeFeatures(attrs['features'])
                if attrs['fabric']:
                    self.changeFabric(attrs['fabric'])
                
        
                try:
                    self.driver.find_elements_by_xpath("//button[contains(text(), 'Apply')]")[0].click()
                except:
                    try:
                        self.driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/form[1]/table/tbody/tr[1]/td/table/tbody/tr/td[1]/button').click()
                    except:
                        apply_script = """document._getElementsByXPath('//*[@id="ssaForm"]/table/tbody/tr[1]/td/table/tbody/tr/td[1]/button')[0].click()"""
                        self.driver.execute_script(apply_script)
                
                print("Applied")
                        
                        
                try:
                    self.driver.find_element_by_link_text('Unlock').click()
                except: 
                    self.driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table[2]/tbody/tr/td[1]/table/tbody/tr[3]/td/table/tbody/tr/td[2]/p[1]/a').click()
                
                print("Unlocked")
                
                self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()                
                
                done = products.pop(0)
                
                print(f"Remaining: {len(products)} products: ", products)
                
        except Exception as error:            
            print(error)
            print('Error: Remaining Pairs: ', products)            
            self.navProducts()
            self.setProductAttributes(products)
    
    def changeName(self, attribute):
        name = self.driver.find_element_by_xpath('//input[@name="Metaf070c9f07840c78a8b2edc1902"]')
        name.clear()                
        name.send_keys(attribute)
        
    def changeWWMT(self, attribute):
        wwmt = self.driver.find_element_by_xpath('//textarea[@id="Meta458a0dcf59c3a300e482bf9054"]')
        wwmt.clear()
        wwmt.send_keys(attribute)
        wwwt2 = self.driver.find_element_by_xpath('//textarea[@id="Meta64da50faa3659f25acdd0d1691"]')
        wwwt2.clear()
        wwwt2.send_keys(attribute)
    
    def changeCareDescription(self, attribute):
        care = self.driver.find_element_by_xpath('//textarea[@name="Metaef8f635ef33efeeecd7ae8c72f"]')
        care.clear()
        care.send_keys(attribute)
        
    def changeFeatures(self, attribute):
        feature = self.driver.find_element_by_xpath('//textarea[@name="Meta482485cfc4b410b57671f7f577"]')
        feature.clear()
        feature.send_keys(attribute)
        
        """WORKING"""
        attr_value = attribute.split('\n')
        script = """
                attr_value = {}
                attr_len = attr_value.length
                for (let i = 0; i < attr_len; i++) {{
                 	container = document.getElementById('Meta525732d56b9c0454ddd1e3aed2_Container')                
                 	inputs = container.getElementsByTagName('input')                
                 	inputs[i].value = attr_value[i]                
                 	add_another = document.getElementById('Meta525732d56b9c0454ddd1e3aed2_lastRow').getElementsByTagName('a')[0]                
                 	add_another.click()                
                }}""".format(attr_value)
        self.driver.execute_script(script)
        
    
    def changeFabric(self, attribute):
        fabric = self.driver.find_element_by_xpath('//input[@id="Meta01b431b006b7e6bf4082c2bc8f_1"]')
        fabric.clear()
        fabric.send_keys(attribute)
        
            
    """ Get Names for #setNames to change Products' Names """    
    def getNames(self, filename):

        names = []

        with open (filename, newline = '', encoding='UTF-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader: 
                
                master = row['master'].strip()
                name = row['name'].strip()
                
                pair = [master, name]
                
                names.append(pair)
                
        print("Changing names: ",names)
        return names
    
    def getProductAttributes(self, filename):

        products = []

        with open (filename, newline = '', encoding='UTF-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader: 
                pair = []
                attrs = {}
                
                master = row['master'].strip()
                # name = row['name'].strip()
                # whyWeMadeThis = row['whyWeMadeThis'].strip()
                # careDescription = row['careDescription'].strip()
                # features = row['features'].strip()
                # fabric = row['fabric'].strip()

                pair.append(master)
                
                attrs['name'] = row['name'].strip()
                attrs['whyWeMadeThis'] = row['whyWeMadeThis'].replace('\n','').strip()
                attrs['careDescription'] = row['careDescription'].strip()
                attrs['features'] = row['features'].strip()
                attrs['fabric'] = row['fabric'].replace('\n','').strip()
                
                pair.append(attrs)
                
                products.append(pair)
                
        print("Changing Attributes: ",products)
        return products
    
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
         
        try:
            self.driver.find_element_by_xpath('//button[@name="PageSize"]')\
                .click()
        except Exception as e:
            print(e)
            # pdb.set_trace()
            try:
                td = self.driver.find_elements_by_class_name('pagecursortxt.top')[-1]
                button = td.find_element_by_xpath('//button[@value="All"]').click()
            except Exception as e: 
                print(e)
                pass
            
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
                print("Applied")
                
                self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()
                
                done = variations.pop(0)
                print("Complete pair -", pair)
        except Exception as error:
            print(error)
            raise
    
    """ Get Styles of Missing Images """
    def getMissingImage(self, filename):
        pairs = []

        with open (filename, newline = '', encoding='UTF-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader: 
                
                try:
                    """ PERSONAL MAC """
                    master = row['master']
                except:
                    """ OFFICE COMPUTER """
                    master = row['\ufeffmaster']
                
                color = row['color']
                style_color = row['style_color']
                
                pair = [master, color, style_color]
                
                pairs.append(pair)
                
        print("Adding Images to > ",pairs)
        return pairs
    
    """ Add Missing Images for Styles"""
    def addMissingImage(self, s, pairs):
        while pairs:    
            pair = pairs[0]

            product = pair[0]
            color = pair[1]
            style_color = pair[2]
            
            # color = color.lower()
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
            
            # pdb.set_trace()
            
            if self.selectColor(color):
                pass
            # Color is hidden and need to add color back
            else:
                self.driver.find_element_by_id('ext-gen98').click()
                sleep(3)
                # pdb.set_trace()
                
                color_options = self.driver.find_elements_by_class_name("x-tree-node-el.x-unselectable.x-tree-node-collapsed.x-tree-node-leaf")
                
                for el in color_options: 
                    if color.lower() in el.get_attribute("innerHTML").lower():
                        el.find_element_by_class_name('x-tree-node-cb').click()
                        popup = self.driver.find_element_by_css_selector('div.x-window-bbar')
                        # button = popup.find_elements_by_css_selector('td.x-btn-center')
                        popup.find_element_by_xpath("//button[contains(text(), 'OK')]").click()
                        self.selectColor(color)
                        break
        
                # try:
                #     idx = soup.find('a').find('span').get('id')
                #     self.driver.find_element_by_id(idx).click()
                #     return True
                # except Exception as e:
                #     print(e)
                #     return False
                
                # table = self.driver.find_element_by_xpath('//*[@id="ext-gen286"]/div/li/ul')
                # li = table.find_elements_by_class_name('x-tree-node')
                
                # for i in range(len(li)):
                #     if color in li[i].get_attribute("innerHTML").lower():
                #         li[i].find_element_by_class_name('x-tree-node-cb').click()
                #         self.driver.find_element_by_id('ext-gen230').click()
                #         self.selectColor(color)

             
            
            
            
            
            # Use to check if first image already exists to avoid adding first image again
            firstMissing = True
            num_rows = 3
            total_img = len(avail_img)
            while avail_img or firstMissing:
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
                
                # Is this a single image issue or no images issue? 
                # Check First image
                if firstMissing:
                    first_box = self.driver.find_element_by_id(ids[0])
                    detail_path = self.driver.find_element_by_id('detail_path')
                
                    first_box.click()
                    
                    # pdb.set_trace()

                    # There is an image in first box, add from _2, and skip this operation in next round
                    if style_color + '_1' in detail_path.get_attribute('value'):
                        # how to get for loop and skip to take care of it
                        done = avail_img.pop(0)
                        firstMissing = False
                        # try with continue
                        continue
                    else:
                        self.driver.find_element_by_id(ids[-1]).click()
                        swatch = img.split("_")[1]
                        if swatch[0:2] == "00":
                            pass
                        else:
                            swatch = swatch[1:]
                        self.driver.find_element_by_id('detail_path').send_keys(swatch)
                        num_rows = 2
                        firstMissing = False
                skip = 1
                for i in range(len(ids)-num_rows):
                    el = self.driver.find_element_by_id(ids[i]).get_attribute('outerHTML')
                    if style_color in el:
                        skip += 1
                        continue
                    elif skip == total_img:
                        skip = 0
                        continue
                    else:
                        self.driver.find_element_by_id(ids[i]).click()
                        self.driver.find_element_by_id('detail_path').send_keys(img)

                
                done = avail_img.pop(0)
                    
            sleep(2)
            
            try:
                save = self.driver.find_elements_by_xpath('//*[@id="ext-gen79"]')
                save.click()
            except:
                self.driver.find_element_by_xpath("//button[contains(text(), 'Save')]")\
                    .click()
            
            done = pairs.pop(0)

            sleep(5)
            
            # pdb.set_trace()
                
            try: 
                self.driver.find_element_by_link_text('Unlock').click()
            except Exception as e:
                # print(e)
                try:
                    sleep(5)
                    self.driver.find_element_by_xpath('//a[contains(text(), "Unlock")]').click()
                except Exception as e:
                    # print(e)
                    unlock = """
                        a = document._getElementsByXPath('//a[contains(text(), "Unlock")]')
                        a[0].click()
                    """
                    self.driver.execute_script(unlock)
                
            print("Applied")
                
            self.driver.find_element_by_xpath('//*[@id="bm-breadcrumb"]/a[3]').click()
                
            print("Complete pair -", pair)
        
    """ Select Color to Add Images to """
    def selectColor(self, color):
        
        # pdb.set_trace()
        
        show_colors = self.driver.find_element_by_css_selector('ul.x-tree-node-ct').find_elements_by_class_name('x-tree-node')
        
        color_search = "color = \'{}\'".format(color.lower())
        # color = \'chrome\'
        
        for el in show_colors: 
            if color_search in el.get_attribute("innerHTML").lower():
                soup = BeautifulSoup(el.get_attribute("innerHTML"), "html.parser")
                break
        
        try:
            idx = soup.find('a').find('span').get('id')
            self.driver.find_element_by_id(idx).click()
            return True
        except Exception as e:
            print(e)
            return False
            
    """ Update Refinement Buckets """
    def getBuckets(self):
        with open('./csv/buckets - JP.csv', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            
            mapping = {}
            
            for row in reader:
                k = row['bucket']
                v = row['style']
                
                if not k:
                    continue 
                
                if k in mapping.keys():
                    mapping[k].append(v)
                else:
                    mapping[k] = [v]
        
        return mapping
    
    def bucketRefinementUpdate(self):
        mapping = self.getBuckets()
        
        urls = input("Enter Category URL(s) > ").splitlines()
        
        # Select last refinement using the attribute type
        attr_types = {
            1: 'By Attribute (Style Number)',
            2: 'By Attribute (ID)',
            3: 'By Attribute (Type)'
            }
        print("(1) By Attribute (Style Number)\n(2) By Attribute (ID)\n(3) By Attribute (Type)")
        index = int(input("Enter Attribute Type > "))
        
        for url in urls:
        
            buckets = list(mapping.keys()) 
            
            self.driver.get(url)
            self.driver.find_element_by_link_text('Search Refinement Definitions').click()
            
            attribute = self.driver.find_elements_by_link_text(attr_types[index])[-1]
            
            self.driver.execute_script("arguments[0].scrollIntoView()", attribute)
            
            attribute.click()
            
            self.selectLanguage()
            
            self.driver.find_element_by_xpath("//body").send_keys(Keys.END)
            
            rows = self.driver.find_elements_by_xpath('//td[@class="table_detail s"]')
            
            # self.driver.execute_script("arguments[0].scrollIntoView()", rows)
            
            while len(rows) > 1:
                self.driver.find_element_by_link_text('Select All').click()
                # self.driver.find_elements_by_xpath('//a[@class="tableheader"]')[0].click()
                try:
                    self.driver.find_element_by_xpath('//button[@name="confirmDelete"]').click()
                except:
                    script = """document._getElementsByXPath('//button[@name="confirmDelete"]')[0].click()"""
                    self.driver.execute_script(script)
                self.driver.find_element_by_xpath('//button[@name="delete"]').click()
                rows = self.driver.find_elements_by_xpath('//td[@class="table_detail s"]')
             
            while buckets:
                bucket_display = buckets[0]
                
                bucket_values = mapping[bucket_display]

                for v in bucket_values:
                    v += ","
                    self.driver.find_element_by_xpath('//input[@name="NewBucketValues"]').send_keys(v)
                # bucket_values = ",".join(mapping[bucket_display])
                
                # self.driver.find_element_by_xpath('//input[@name="NewBucketValues"]').send_keys(bucket_values)
                
                self.driver.find_element_by_xpath('//input[@name="NewBucketDisplay"]').send_keys(bucket_display)
                
                try:
                    self.driver.find_element_by_xpath('//button[@name="add"]').click()
                except:
                    script = """document._getElementsByXPath('//button[@name="add"]')[0].click()"""
                    self.driver.execute_script(script)
                
                print("Done > {}".format(bucket_display))
                
                done = buckets.pop(0)
        
        

        
        
        
    def skuAttrUpdate(self):
        self.navProducts()
        mapping = skuAttributeRefinement()
        
        # mapping = {['sample:True]: ['119350036','119350038','119350038']}
        
        # pdb.set_trace()
        
        for k, v in mapping.items():
        # Get SKUs from CSV
            if len(v) > 10000:
                n = len(v) / 10000
                
                while n > 0:
                    self.searchProducts((",").join(v[0:10000]))
                    # execute
                    self.changeAttribute(k)
                    del v[0:10000]
                    n -=1 
            else:
                self.searchProducts((",").join(v))
                # execute
                self.changeAttribute(k)
    
    def selectIndexName(self, index, selectname):
        select_script = """document._getElementsByXPath('//select[@name="{}"]')[0].selectedIndex = {}""".format(selectname, index)
        self.driver.execute_script(select_script)
    
    def changeAttribute(self, k):
        self.editAll_ProductTool()
        self.driver.find_element_by_xpath("//input[@value='UpdateProductAttributes']").click()
        self.driver.find_element_by_xpath('//button[@name=\"selectAction\"]').click()
        self.driver.find_element_by_link_text('Select attributes').click()        
        # main window
        default_handle = self.driver.current_window_handle
        handles = list(self.driver.window_handles)
        handles.remove(default_handle)
        
        # Focus on pop up window
        self.driver.switch_to.window(handles[0])
        all_button = """
                    button = document._getElementsByXPath('//button[@name="PageSize"]');
                    button[button.length -1].click()
                """
        try:
            self.driver.execute_script(all_button)                
        except: 
            pass
        
        data = k.split(":")
        attr_id,  attr_value = data
        
        attribute_select = """
                input = document._getElementsByXPath('//input[@value="{}"]');
                input[1].click()
        """.format(attr_id)
        
        # pdb.set_trace()
        
        # Attrribute we are changing
        self.driver.execute_script(attribute_select)
        self.driver.find_element_by_xpath('//button[@name="apply"]').click()
        # # Close pop-up window
        # self.driver.close()
        # Return focus to Main Window
        self.driver.switch_to.window(default_handle)
        
        
        if "searchRank" in attr_id:
            # pdb.set_trace()
            self.changeSearchAttributes("ranking", attr_value)
        if "searchPlacement" in attr_id:
            self.changeSearchAttributes("placement", attr_value)
                
        if "onlineFlag" == attr_id:
            self.changeOnlineAttributes("online", attr_value)
        if "onlineFrom" == attr_id:
            self.changeOnlineAttributes("online_from", attr_value)
        if "onlineTo" == attr_id:
            self.changeOnlineAttributes("online_to", attr_value)

        if "gender" in attr_id:
            self.driver.find_element_by_xpath('//input[@name="Metaacd6c76f44f5a3f7627fb8fde2"]').send_keys(attr_value)
        
        try:
            # find language 
            if self.driver.find_element_by_xpath('//select[@id="languageSelector"]'):
                self.selectLanguage()
        except:
            # attribute requires no langage
            pass
    
        try:
            # attribute uses input
            # send keys to set attribute
            attr_value = attr_value.replace('\n','').strip()
            self.driver.find_element_by_class_name('inputfield_en.w100.perm_localized').send_keys(attr_value)
        except:
            # attribute does not use input
            pass
        
        if "bra" in attr_id:
            try:
                bra_support = {
                    'High': 1,
                    'Medium': 2,
                    'Low': 3
                    }
                index = bra_support[attr_value]
                self.selectIndexName(index, "Meta28f81c2f03d5405447b81d1655")
                # select_script = """document._getElementsByXPath('//select[@name="Meta28f81c2f03d5405447b81d1655"]')[0].selectedIndex = {}""".format(index)
                # self.driver.execute_script(select_script)
            except:
                pass

        if "cup" in attr_id:
            try:
                cup_size = {
                    'A/B': 1,
                    'A-E': 2,
                    'B/C': 3,
                    'C/D': 4,
                    'C-E': 5
                    }
                index = cup_size[attr_value]
                self.selectIndexName(index, "Metaa8f457318b6f96eaf269e4995e")
            except:
                pass
            
        
        # Change Attribute
        change = """document._getElementsByXPath('//button[@name="updateProductAttributesAndReturn"]')[0].click()"""

        try:
            self.driver.find_element_by_xpath('//button[@name="updateProductAttributesAndReturn"]').click()
        except:
            self.driver.execute_script(change)

    def changeOnlineAttributes(self, option, attr_value):
        online = {
            'HK': 'Metafcc2f3c3cad3b20d4cd1fbac76_7b4d0d9edde1e19b6742fff72e',
            'JP': 'Metafcc2f3c3cad3b20d4cd1fbac76_b7ab540a8dccb8a8576e3f937e'
            }
        
        online_from = {
            'HK': 'Meta4fbf379d4d2a1a1105f19f9d8a_7b4d0d9edde1e19b6742fff72e',
            'JP': 'Meta4fbf379d4d2a1a1105f19f9d8a_b7ab540a8dccb8a8576e3f937e'
            }
        online_choice = {
            'Yes': 1,
            'No': 0
            }
        online_to = {
            'HK': "Metaa7b2b559c046e5d30bc3f5b8b3_7b4d0d9edde1e19b6742fff72e",
            'JP': "Metaa7b2b559c046e5d30bc3f5b8b3_b7ab540a8dccb8a8576e3f937e"
            }
        
        if option == "online":
            inputid = online[self.site]
        elif option == "online_from":
            inputid = online_from[self.site]
        elif option == "online_to":
            inputid = online_to[self.site]
            
        # Select Site
        self.driver.find_element_by_xpath('//input[@id="{}_AttrRow"]'.format(inputid)).click()
        
        if option == "online_from" or option == "online_to":
            self.driver.find_element_by_xpath('//input[@id="{}"]'.format(inputid)).send_keys(attr_value)
            # 10/22/2020 12:00 am
            
            self.driver.find_element_by_xpath('//input[@id="{}"]'.format(inputid+'2')).send_keys("12:00 am")


        else:
            choice = online_choice[attr_value]
            select_script = """document._getElementsByXPath('//select[@id="{}"]')[0].selectedIndex = {}""".format(inputid, choice)
            self.driver.execute_script(select_script)
        
        return

        
        
    def changeSearchAttributes(self, option, attr_value):
        searchPlacementSite = {
            'HK': 'Meta01d58528fe74cc8798d32681ab_7b4d0d9edde1e19b6742fff72e',
            'JP': 'Meta01d58528fe74cc8798d32681ab_b7ab540a8dccb8a8576e3f937e'
            }
        
        searchRankSite = {
            'HK': 'Meta32665f3e2ab9427d9688d1dca5_7b4d0d9edde1e19b6742fff72e',
            'JP': 'Meta32665f3e2ab9427d9688d1dca5_b7ab540a8dccb8a8576e3f937e'
            }
               
        if option == "placement":
            inputid = searchPlacementSite[self.site]
        elif option == "ranking":
            inputid = searchRankSite[self.site]
            
        # Select Site
        self.driver.find_element_by_xpath('//input[@id="{}_AttrRow"]'.format(inputid)).click()
        
        # pdb.set_trace()
        
        # Select Attribute Value
        select_script = """
            select = document._getElementsByXPath('//select[@name="{}"]')[0] 
            options = select.options
            length = options.length
                
            for (i = 0; i < length; i++) {{
                    if (options[i].value === '{}') {{
                            select.selectedIndex = i;
                            break;
                    }}
            }}
        """.format(inputid, attr_value)
        self.driver.execute_script(select_script)
        
        return
        
        

##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### ##### SEO SCRIPTS ##### 

    def hreflang(self):
        
        self.driver.get('https://staging-eu01-lululemon.demandware.net/on/demandware.store/Sites-Site/default/ViewChannelCatalogList_52-Start?SelectedMenuItem=prod-cat&CurrentMenuItemId=prod-cat&screen=catalog')
        
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
        
        self.seo_filename = './csv/logs/' + self.site + "_BM_categories_new.csv"
        
        with open(self.seo_filename, "w", encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID','Hreflangtag', 'Edit link'])
           
        try:
            self.driver.find_element_by_xpath('//button[@name=\"CategoryPageSize\"]').click()
        except:
            try:
                script = """
                document._getElementsByXPath('//button[@name=\"CategoryPageSize\"]')[0].click()
                """
                self.driver.execute_script(script)
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
            
    def catalog_crawl(self, link):
        self.driver.get(link)
        
        try:
            self.driver.find_element_by_xpath('//button[@name=\"CategoryPageSize\"]').click()
        except:
            try:
                script = """
                document._getElementsByXPath('//button[@name=\"CategoryPageSize\"]')[0].click()
                """
                self.driver.execute_script(script)
            except: 
                pass
                      
        cdp_button = """
                table = document._getElementsByXPath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td/form[2]/table/tbody/tr/td/table[1]');
                links = table[0].querySelectorAll('.table_detail_link');
                array = Array.prototype.slice.call(links);
                return array.map(link=>link.href);
        """
        try:
            cdp_links = self.driver.execute_script(cdp_button)
            cdp_links = list(set(cdp_links))
            
        except:
            cdp_links = []
            
        self.category_attr_crawl(link)       
               
        print("CDP Links -",len(cdp_links))
        return cdp_links

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
        
    def openCGIDlinks(self):
        cgIds = []
        previewURL = 'https://staging-eu01-lululemon.demandware.net/on/demandware.store/Sites-Site/default/ViewStorefront-Catalog?cgid='
        
        filename = './csv/logs/' + self.site +'_BM_Categories_new.csv'
        with open(filename, newline = '', encoding = 'utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                try:
                    cgId = row['ID'].strip()
                except:
                    cgId = row['\ufeffID'].strip()
                cgIds.append(cgId)
        
        total = len(cgIds)
        counter = 1
            
        filename = './csv/logs/' + self.site + '_staginglinks.csv'
        
        with open(filename, "w", encoding = 'utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['categoryID', 'new_url'])
            
            # break point to allow Oauth login in alert window
            link = previewURL + cgIds[0]
            self.driver.get(link)
            
            pdb.set_trace()
            
            for cgId in cgIds:
                link = previewURL + cgId
                self.driver.get(link)
                
                checkReadiness = """
                    return document.readyState
                """
                
                ready = self.driver.execute_script(checkReadiness)
                
                while ready != "complete":
                    sleep(3)
                    ready = self.driver.execute_script(checkReadiness)
                    
                currURL = self.driver.current_url
                
                print("{}/{}".format(counter, total))
                
                counter += 1
                
                writer.writerow([cgId, currURL])
                
                

        
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
    
    def getBMLinks(self):
        
        filename = './csv/logs/' + self.site + '_BM_categories.csv'
        
        with open (filename, newline = '', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            hashes = {}
            for row in reader: 
                category = row['ID'].strip()
                link = row['Edit link'].strip()
                hashes[category] = link
        
        return hashes
    
    def navigateSEO(self, option = None):
        
        if not option: 
            option = self.site
        
        self.driver.find_element_by_link_text('Category Attributes').click()
        self.selectLanguage(option)
    
    def getSEOCopy(self, filename):
        with open (filename, newline = '', encoding='UTF-8-SIG') as csvfile:
            reader = csv.DictReader(csvfile)
            hashes = {}
            for row in reader:
                link = row['edit_link'].strip()
                copy = row['copy']
                hashes[link] = copy
        
        return hashes
    
    
    def germanCDPCopy(self):
        
        CDPCopy = './csv/seo/german_luxembourg_cdp_copy.csv'
        
        # "german_switzerland_cdp_copy.csv",
        # "german_luxembourg_cdp_copy.csv",
        # "german_german_cdp_copy.csv"
        
        MetaDescCopy = './csv/seo/german_metadesc_copy.csv'
        
        mapping = self.getSEOCopy(CDPCopy)
        second_mapping = self.getSEOCopy(MetaDescCopy)
        pages_with_meta = list(second_mapping.keys())
        
        # pdb.set_trace()
        
        for k, v in mapping.items():
            self.driver.get(k)
            
            
            if k in pages_with_meta:
                description = second_mapping[k]
                self.navigateSEO('DE')
                textarea = self.driver.find_element_by_xpath('//*[@name="Meta1ec359d1cf783abc4a30a0ae48"]')                
                textarea.clear()                
                textarea.send_keys(description)
                self.applyCat_Attr()
            
            self.selectLanguage('DE_LX')            
            textarea = self.driver.find_element_by_xpath('//*[@id="Metab9e2492ca65e0828f9c4b28da7"]')                
            textarea.clear()                
            textarea.send_keys(v)
            
            self.applyCat_Attr()
        
    def getSEOContents(self, hashes):
        filename = self.createSEOContentsCSV()
        for cat, link in hashes.items():    
            self.driver.get(link)
            
            self.navigateSEO()
            
            try:
                page_title = self.driver.find_element_by_id('Meta99f94788870eca46e563b8e4d6').get_attribute('value')
            except: 
                page_title = ''
            try:
                page_desc = self.driver.find_element_by_id('Meta1ec359d1cf783abc4a30a0ae48').get_attribute('value')
            except: 
                page_desc = ''
            try:
                page_add_content = self.driver.find_element_by_id('Metab9e2492ca65e0828f9c4b28da7').get_attribute('value')
            except:
                page_add_content = ''
            
            content = [cat, link, page_title, page_desc, page_add_content]
            
            self.writeSEOContents(filename, content)
    
    def createSEOContentsCSV(self):
        filename = './csv/logs/' + self.site + '_Additional_SEO_Content.csv'
        with open(filename, "w", newline = '', encoding='UTF-8') as f: 
            writer = csv.writer(f)
            writer.writerow(["ID", "Edit link", "Title", "Desc", "Additional"])
            f.close()
        return filename
    
    def writeSEOContents(self, filename, content):
        with open(filename, "a", newline = '', encoding='UTF-8') as f: 
            writer = csv.writer(f)
            writer.writerow(content)
            f.close()
        return
    
    def applyCat_Attr(self):
        try:
            self.driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/form[1]/table/tbody/tr[2]/td/table/tbody/tr/td[1]/button').click()
            print("Applied")
        except Exception as e:
            # print(e)
            apply_script = """
                document._getElementsByXPath('//*[@id="bm_content_column"]/table/tbody/tr/td/table/tbody/tr/td[2]/form[1]/table/tbody/tr[2]/td/table/tbody/tr/td[1]/button')[0].click()
            """
            self.driver.execute_script(apply_script)
            print("Applied")
    
    def updateAdditionalSEO(self, filename):
        with open(filename, newline = '', encoding='ISO-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader: 
                url = row['Edit link']
                print(url)
                new = row['New_Additional']
                print(new)
                self.driver.get(url)
                self.navigateSEO()
                old_content = self.driver.find_element_by_id('Metab9e2492ca65e0828f9c4b28da7')
                old_content.clear()
                old_content.send_keys(new)
                self.applyCat_Attr()
                
    def specifiedURL(self, filename):
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            
            for row in reader:
                try:
                    cg_id = row['\ufeffcg_id'].strip()
                except:
                    cg_id = row['cg_id'].strip()
                edit_link = row['edit_link'].strip()
                specified_URL = row['specified_url'].strip()
                
                self.driver.get(edit_link)
                
                self.navigateSEO()
                
                # pdb.set_trace()
                
                page_url_input = self.driver.find_element_by_xpath("//input[@name=\"Meta148f83610341e6d46c3bb5e0b3\"]")
        
                page_url_input.clear()
                
                page_url_input.send_keys(specified_URL)
                
                self.applyCat_Attr()
                
                print(cg_id)
      
    def updateHrefCatAttr(self):
        pairs = getPairs()
                
        with open("./csv/seo/all_hreflangs.csv", encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader: 
                edit_link = row['edit_link']
                self.driver.get(edit_link)
                self.driver.find_element_by_link_text('Category Attributes').click()
                
                # pdb.set_trace()
                
                href_lang_input = self.driver.find_element_by_xpath('//*[@id="Meta12caa1c79d61919817dda9fecd"]')
                
                old_tag = href_lang_input.get_attribute('value')
                new_tag = old_tag 
                
                for pair in pairs:
                    if pair[0] in new_tag: 
                        new_tag = new_tag.replace(pair[0], pair[1])
                        print("{} => {}".format(pair[0],pair[1]))
                        print("Replaced!")
                
                href_lang_input.clear()
                
                href_lang_input.send_keys(new_tag)
                
                self.applyCat_Attr()
            
    
""" Clean up Hrefs in CSV """    
def checkHrefs():
    with open("./csv/hreflangtags.txt", encoding='utf-8') as file:
        contents = file.read()
        soup = BeautifulSoup(contents, "html.parser")
        # print(soup)
        links = soup.find_all('link')
        # print(links)
        file_href = [l.get('href') for l in links]
        file_href = list(set(file_href))
        print(file_href)
    with open('./csv/logs/old_to_new_links.csv', "w", newline = '', encoding='UTF-8') as f:
        writer = csv.writer(f)
        writer.writerow(["old", "new", "status"])
        s = requests.Session()
        s.get('https://staging-eu01-lululemon.demandware.net/s/JP/ja-jp/home', auth=HTTPBasicAuth(email, password))
        
        for href in file_href:
            try:
                response = s.get(href)
            except: 
                writer.writerow([href])
                continue
            status = response.status_code
            new_url = response.url
            print("{} => {}".format(href, new_url))
            writer.writerow([href, new_url, status])
            

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

def extractHref(filename):
    file_href = []
    with open (filename, newline = '', encoding='UTF-8') as csvfile:
        reader = csv.DictReader(csvfile)
        record = []
        for row in reader: 
            record.append(row['Additional'])
        string_record = " ".join(record)
        soup = BeautifulSoup(string_record, "html.parser")

        anchors = soup.find_all('a')
        file_href = [a.get('href') for a in anchors]

    with open('./csv/logs/old_to_new_links.csv', "w", newline = '', encoding='UTF-8') as f:
        writer = csv.writer(f)
        writer.writerow(["old", "new", "status"])
        s = requests.Session()
        for href in file_href:
            response = s.get(href)
            status = response.status_code
            new_url = response.url
            print("{} => {}".format(href, new_url))
            writer.writerow([href, new_url, status])
        
def replaceHref():
      with open("./csv/seo/HK_additional_contents.csv", newline = '', encoding='UTF-8') as csvfile:
          reader = csv.DictReader(csvfile)
          pairs = getPairs()
          
          with open("./csv/seo/new_HK_additional_contents.csv", "w", encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Edit link", "Additional", "New_Additional"])
        
            for row in reader:
                try:
                    ID = row['\ufeffID'].strip()
                except:
                    ID = row['ID'].strip()
                
                edit_link = row['Edit link'].strip()
                
                old = row['Additional'].strip()
                
                new = old
                
                for pair in pairs:
                    if pair[0] in new: 
                        new = new.replace(pair[0], pair[1])
                        print("{} => {}".format(pair[0],pair[1]))
                 
                writer.writerow([ID, edit_link, old, new])    

    
    
##### MAIN SCRIPTS ##### ##### MAIN SCRIPTS ##### ##### MAIN SCRIPTS ##### ##### MAIN SCRIPTS ##### ##### MAIN SCRIPTS ##### ##### MAIN SCRIPTS ##### ##### MAIN SCRIPTS ##### 



""" Creating instance of SFbot 🤖 """
site = input("Enter Site > ").strip()
my_bot = SFBot(email, password, site)

# urls = input("urls > ").splitlines()
# for u in urls: 
#     my_bot.driver.get(u)
#     my_bot.expandCategoryPosition()
#     my_bot.categoryPositionClear()
#     my_bot.updatePositionsButton()

"""Update Category Position 😊 """
# my_bot.categoryPosition()

"""Bucket Refinements"""
# my_bot.bucketRefinementUpdate()

""" Assign Multi Categories 😊 """
# catFile = './csv/categories_' + site + '.csv'
# categories = my_bot.getCategories(catFile)
# primary = categories[0]
# secondary = categories[1]
# my_bot.navProducts()
# my_bot.setCategories(primary, secondary)

""" Changing Multi Product Descriptions 😊 """
# products = my_bot.getProductAttributes('./csv/names.csv')
# my_bot.navProducts()
# my_bot.setProductAttributes(products)


""" Just names (depracating) """
# names = my_bot.getNames('./csv/names.csv')
# my_bot.setNames(names)

""" Batch Update Product Attributes 😊 """
# my_bot.skuAttrUpdate()

""" Delete Multi Sale Prices 😊 """
# pricebooks = {
#     '1': '40188-HKD-SALE',
#     '2': 'EMP-HKD-PROMO',
#     '3': '49188-JPY-SALE',
#     '4': 'EMP-JPY-PROMO',
#     '5': '59188-AUD-SALE',
#     '6': '55188-NZD-SALE'
#     }
# print("Pricebooks:\n(1)HKD SALE\n(2)HKD EMP\n(3)JPY SALE\n(4)JPY EMP\n(5)AUD SALE\n(6)NZD SALE")
# choice = input("Enter PriceBook > ").strip()
# priceBook = pricebooks[choice]
# skus = my_bot.getSkus('./csv/skus.csv')
# my_bot.navPriceBook(priceBook)
# my_bot.deletePrice(skus)


""" Create Variant Groups 😊 """ 
# variations = my_bot.getVariations('./csv/variations.csv')
# my_bot.navProducts()
# my_bot.createVariants(variations)


""" Return Search Results in CSV 😢 """
# my_bot.navProducts()
# products = [x.strip() for x in input("Enter Products > ").splitlines()]
# products = list(dict.fromkeys(products))
# my_bot.copyProductStatus(products)


""" Change front color 😢 """
"""Missing ability to use the first color in list as front"""
# variations = my_bot.getFrontColor('./csv/colors.csv')
# my_bot.navProducts()
# my_bot.updateFrontColor(variations)


""" Add missing images 😢 """
# product = 'prod9850150'
# color = "Heathered Mod Faint Coral"
# style_color = 'LW3BZVS-037724'
# pairs = [[product, color, style_color]]

# my_bot.navProducts()
# s = requests.Session()
# pairs = my_bot.getMissingImage('./csv/missing_images.csv')
# my_bot.addMissingImage(s, pairs)



# # # SEO SCRIPTS # # # SEO SCRIPTS # # # SEO SCRIPTS # # # SEO SCRIPTS # # # SEO SCRIPTS # # # SEO SCRIPTS # # # SEO SCRIPTS # # # SEO SCRIPTS # # # 

""" Recursive HRefLang Crawl 😊 """
# my_bot.hreflang()

""" Update all regions Href """
# checkHrefs()
# my_bot.updateHrefCatAttr()
# my_bot.openCGIDlinks()

""" Change Page URL (Japan) """
# filename = './csv/seo/japan_page_url.csv'
# my_bot.specifiedURL(filename)


""" HRefland Update 😊 """
# updateHrefCSV()
# my_bot.updateHref('./csv/seo/new_href_langtag.csv')


""" Open XX_BM_categories """
# categories = my_bot.getBMLinks()
# my_bot.getSEOContents(categories)


"""Extract href from Additional SEO Content """
# filename = './csv/logs/' + input("Enter filename > ").strip() + '.csv'
# extractHref(filename)
# replaceHref()
# filename = './csv/seo/new_HK_additional_contents.csv'
# my_bot.updateAdditionalSEO(filename)


""" Open Category IDs in BM to get Current Staging Links """
# urls = [['women-collections-lab', 'https://staging-eu01-lululemon.demandware.net/on/demandware.store/Sites-Site/default/ViewStorefront-Catalog?cgid=women-collections-lab']]
# my_bot.openCGIDlinks()

"""Update German Copy for Page Description and Additional SEO Content """
# my_bot.germanCDPCopy()

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
#     my_bot = SFBot(email, pw, site)    
#     action = input("What do you want? -")
#     cases = {
#         'q': my_bot.driver.quit()
#     }
#     cases[action]
#     if action == "q":
#         running = False

# curr_dir = os.path.dirname(os.path.realpath(__file__))
# print(curr_dir)

# split = os.path.split(curr_dir)[0]
# csv_dir = split + '\csv'
# print(csv_dir)

# parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(parent_dir)

