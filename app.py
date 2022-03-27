from flask import Flask, render_template, \
    Response, jsonify, request, json
import os
from datetime import datetime
import sys
import base64
import mechanicalsoup
from bs4 import BeautifulSoup
import requests
import shutil

app = Flask(__name__)

global items_list
items_list = None


def log_visitor():
    visitor_ip = request.remote_addr
    visitor_requested_path = request.full_path
    now = datetime.now()
    dt = now.strftime("%d/%m/%Y %H:%M:%S")

    pth = os.path.dirname(os.path.abspath(__file__))
    f = open(os.path.join(pth,"log.txt"), "a")
    f.write(dt + ": " + str(visitor_ip) + " " + str(visitor_requested_path) + "\n")
    f.close()

@app.route('/')
@app.route('/index')
def index():
    global items_list
    log_visitor()
    if(items_list is None):
        #download_images();
        populate_items();
        
    return render_template('index.html', items_list=items_list) 

def download_images():
    url = "https://thecyclefrontier.fandom.com/wiki/Loot"
    page = requests.get(url)
    
    soup = BeautifulSoup(page.text)
    rows = soup.find("div", {"id" : "content"}).find("tbody").find_all("tr")
    
    for row in rows:        
        cells = row.find_all("td")
        
        if(len(cells) > 0):
            if(cells[1].string is None):
                if(cells[1].find("span") is not None):
                    name = cells[1].find("span").string.strip()
                elif(cells[1].find("a") is not None):
                    name = cells[1].find("a").string.strip()
            else:                
                name = cells[1].string.strip()
                
            if(cells[0].find("img") is not None):
                print(cells[0])
                image_src = cells[0].find("a")['href']
                img = requests.get(image_src, stream=True)
                with open(os.path.join(os.getcwd(), "static", "img", 
                          name+".png"), 'wb') as f:
                    img.raw.decode_content = True
                    shutil.copyfileobj(img.raw, f) 
                
def populate_items():
    global items_list
    items_list = []
    url = "https://thecyclefrontier.fandom.com/wiki/Loot"
    browser = mechanicalsoup.Browser()
    page = browser.get(url)
    
    soup = page.soup
    rows = soup.find("div", {"id" : "content"}).find("tbody").find_all("tr")
    
    item_no = 0
    for row in rows:        
        cells = row.find_all("td")
        name = ""
        link = ""
        image_src = ""
        weight = ""
        sell_price = ""
        price_per_weight =""
        
        if(len(cells) > 0):
            if(cells[1].string is None):
                if(cells[1].find("span") is not None):
                    name = cells[1].find("span").string.strip()
                elif(cells[1].find("a") is not None):
                    name = cells[1].find("a").string.strip()
                    link = cells[1].find("a", href=True)['href']
                    link = link.replace("/wiki", 
                            "https://thecyclefrontier.fandom.com/wiki")
            else:                
                name = cells[1].string.strip()
            
            if(cells[0].find("img") is not None):
                image_src = "img/"+name+".png"

            if(cells[2].string is not None):
                weight = cells[2].string.strip()
                
            if(cells[3].string is not None):
                sell_price = cells[3].string.strip()
                
            if(cells[4].string is not None):
                price_per_weight = cells[4].string.strip() 
               
            #print(f"{name}: {link} {weight} {price_per_weight}")
            item = {
                "id":str(item_no),
                "name":name,
                "link":link,
                "image_src":image_src,
                "weight":weight,
                "price_per_weight":price_per_weight,
                "sell_price":sell_price
            }
            items_list.append(item)
            item_no += 1
    
if __name__ == '__main__':
    #app.run(host='127.0.0.1',debug=True,port="12345")
    app.run(host='0.0.0.0',debug=False,port="80")