import json
import requests
from bs4 import BeautifulSoup
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
url="https://api.nhathuoclongchau.com.vn/lccus/search-product-service/api/products/ecom/product/search/cate"
payload = {
    "skipCount": 0,
    "maxResultCount": 10,
    "category": ["thuoc/thuoc-di-ung"],
    "codes": [
        "productTypes", "priceRanges", "prescription", "objectUse", 
        "skin", "flavor", "manufactor", "indications", "brand", 
        "brandOrigin", "producer", "specification", "ingredient"
    ],
    "sortType": 4
}

re=requests.post(url=url,headers=headers,json=payload)
datan=re.json()

for i in range(len(datan["products"])):
      infor = f'https://nhathuoclongchau.com.vn/{datan["products"][i]["slug"]}'
      res = requests.get(url=infor,headers=headers)
      if res.status_code == 200:
        html = BeautifulSoup(res.content, "html.parser")
        kq = html.find("div", class_="usage")
        if kq:
            mota= kq.get_text(separator=' ',strip=True)
            datan["products"][i]["mota"]=mota
        ue = html.find("div", class_="dosage")
        if ue:
            huong_dan= ue.get_text(separator=' ',strip=True)
            datan["products"][i]["huongdan"]=huong_dan
with open("data.json","w",encoding="utf-8") as b:
        json.dump(datan,b,indent=4,ensure_ascii=False)


