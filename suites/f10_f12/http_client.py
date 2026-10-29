"""Stateful HTTP functional checks; deliberately not labelled browser/UI tests."""
import json
from pathlib import Path
from urllib.parse import parse_qs,urlparse
import requests
from bs4 import BeautifulSoup

class ApiShop:
    def __init__(self,base,output,sid):
        self.base,self.output,self.sid=base.rstrip("/")+"/",Path(output),sid
        self.session=requests.Session()
        self.events=[]
        self.evidence=[]
    def request(self,route,data=None,sensitive=False):
        url=self.base+"index.php?route="+route
        r=self.session.get(url,timeout=35) if data is None else self.session.post(url,data=data,timeout=35)
        r.raise_for_status()
        try:body=r.json()
        except ValueError:
            p=BeautifulSoup(r.text,"html.parser")
            body=(p.select_one("#content") or p).get_text(" ",strip=True)[:12000]
        self.events.append(dict(method="GET" if data is None else "POST",route=route,url=r.url,status=r.status_code,response="[account setup response omitted]" if sensitive else body))
        return r
    def capture(self,label):
        name=f"{self.sid}-{label}.json"
        (self.output/name).write_text(json.dumps(self.events,indent=2,ensure_ascii=False),encoding="utf-8")
        if name not in self.evidence:self.evidence.append(name)
    def page(self,route):
        r=self.request(route)
        return BeautifulSoup(r.text,"html.parser")
    def register(self,email,password):
        self.page("account/register")
        r=self.request("account/register",dict(customer_group_id=1,firstname="A3",lastname="Test",email=email,telephone="0200000000",password=password,confirm=password,newsletter=0,agree=1),sensitive=True)
        assert "account/success" in r.url,"HTTP account setup did not reach success."
    def login(self,credentials):
        r=self.request("account/login",dict(email=credentials[0],password=credentials[1]),sensitive=True)
        assert "account/account" in r.url,"HTTP login prerequisite failed."
    def add_wishlist(self,pid):
        body=self.request("account/wishlist/add",dict(product_id=pid)).json()
        assert "success" in body,"Wishlist add must return a success response."
    def wishlist(self):
        p=self.page("account/wishlist")
        rows=p.select("#content table tbody tr")
        return {int(parse_qs(urlparse(a["href"]).query)["product_id"][0]):row for row in rows if (a:=row.select_one('a[href*="product_id="]'))}
    def remove_wishlist(self,pid):
        self.request("account/wishlist&remove="+str(pid))
    def clear_wishlist(self):
        for pid in list(self.wishlist()):self.remove_wishlist(pid)
    def add_compare(self,pid):
        body=self.request("product/compare/add",dict(product_id=pid)).json()
        assert "success" in body
    def comparison(self):
        p=self.page("product/compare")
        return p,[int(parse_qs(urlparse(a["href"]).query)["product_id"][0]) for a in p.select('#content table tbody tr:first-child a[href*="product_id="]')]
    def add_cart(self):
        body=self.request("checkout/cart/add",dict(product_id=40,quantity=1)).json()
        assert "success" in body,"Cart prerequisite failed."
    def guest_form(self):
        self.add_cart()
        self.page("checkout/checkout")
        self.page("checkout/login")
        return self.page("checkout/guest")
