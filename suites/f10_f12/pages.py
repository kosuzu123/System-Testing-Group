"""OpenCart UI actions. All state changes use normal page controls."""
from pathlib import Path
from urllib.parse import parse_qs,urlparse
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select,WebDriverWait

class Shop:
    def __init__(self,driver,base,output=None,sid="setup"):
        self.driver,self.base=driver,base.rstrip("/")+"/"
        self.wait,self.output,self.sid=WebDriverWait(driver,25),output,sid
        self.evidence=[]
    def idle(self):
        self.wait.until(lambda d:d.execute_script('return document.readyState==="complete" && (!window.jQuery || jQuery.active===0)'))
    def open(self,route):
        self.driver.get(self.base+"index.php?route="+route)
        self.idle()
    def click(self,css):
        e=self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,css)))
        self.driver.execute_script('arguments[0].scrollIntoView({block:"center"});',e)
        e.click()
        self.idle()
    def fill(self,css,text):
        e=self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,css)))
        e.clear()
        e.send_keys(text)
    def capture(self,label):
        if self.output:
            name=f"{self.sid}-{label}.png"
            self.driver.save_screenshot(str(Path(self.output)/name))
            if name not in self.evidence:self.evidence.append(name)
    def register(self,email,password):
        self.open("account/register")
        for field,value in dict(firstname="A3",lastname="Test",email=email,telephone="0200000000",password=password,confirm=password).items():
            self.fill("#input-"+field,value)
        self.click('input[name="newsletter"][value="0"]')
        self.click('input[name="agree"]')
        self.click('#content input[type="submit"]')
        assert "account/success" in self.driver.current_url,"Account setup registration failed."
    def login(self,account):
        self.open("account/login")
        self.fill("#input-email",account[0])
        self.fill("#input-password",account[1])
        self.click('#content input[type="submit"]')
        assert "account/account" in self.driver.current_url,"Login prerequisite failed."
    def product(self,pid):
        self.open("product/product&product_id="+str(pid))
        self.wait.until(EC.visibility_of_element_located((By.ID,"button-cart")))
    def add_list(self,kind,pid):
        self.product(pid)
        self.click(f'#content button[onclick="{kind}.add(\'{pid}\');"]')
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,".alert-success")))
    def wishlist_rows(self,pid):
        return self.driver.find_elements(By.XPATH,f'//*[@id="content"]//table//tbody/tr[td/a[contains(@href,"product_id={pid}")]]')
    def clear_wishlist(self):
        self.open("account/wishlist")
        while self.driver.find_elements(By.CSS_SELECTOR,"#content a.btn-danger"):
            self.click("#content a.btn-danger")
    def remove_wishlist(self,pid):
        rows=self.wishlist_rows(pid)
        assert len(rows)==1
        rows[0].find_element(By.CSS_SELECTOR,"a.btn-danger").click()
        self.idle()
    def comparison_ids(self):
        links=self.driver.find_elements(By.CSS_SELECTOR,'#content table tbody tr:first-child a[href*="product_id="]')
        return [int(parse_qs(urlparse(a.get_attribute("href")).query)["product_id"][0]) for a in links]
    def guest_form(self):
        self.product(40)
        self.click("#button-cart")
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,".alert-success")))
        self.open("checkout/checkout")
        self.click('input[name="account"][value="guest"]')
        self.click("#button-account")
        self.wait.until(EC.visibility_of_element_located((By.ID,"input-payment-firstname")))
    def complete_guest(self):
        data={"firstname":"A3","lastname":"Test","email":"a3.guest@example.com","telephone":"0200000000","address-1":"1 Test Street","city":"Sydney","postcode":"2000"}
        for field,value in data.items():self.fill("#input-payment-"+field,value)
        Select(self.driver.find_element(By.ID,"input-payment-country")).select_by_visible_text("Australia")
        # AJAX replaces the options: re-find and select on every poll.
        def select_requested_zone(driver):
            try:
                zone=Select(driver.find_element(By.ID,"input-payment-zone"))
                zone.select_by_visible_text("New South Wales")
                return zone.first_selected_option.text.strip()=="New South Wales"
            except (NoSuchElementException, StaleElementReferenceException):
                return False
        self.wait.until(select_requested_zone)
        self.capture("guest-valid-data")
        self.click("#button-guest")
