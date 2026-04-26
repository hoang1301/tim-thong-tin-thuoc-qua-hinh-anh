import json
import requests
from bs4 import BeautifulSoup
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
url="https://api.nhathuoclongchau.com.vn/lccus/search-product-service/api/products/ecom/product/search/cate"
list=[
    "thuoc/thuoc-di-ung",
    "thuoc/thuoc-giai-doc-khu-doc-va-ho-tro-cai-nghien",
    "thuoc/thuoc-da-lieu",
    "thuoc/mieng-dan-cao-xoa-dau",
    "thuoc/co-xuong-khop",
    "thuoc/thuoc-bo-and-vitamin",
    "thuoc/thuoc-dieu-tri-ung-thu",
    "thuoc/thuoc-giam-dau-ha-sot-khang-viem",
    "thuoc/thuoc-ho-hap",
    "thuoc/thuoc-khang-sinh-khang-nam",
    "thuoc/thuoc-mat-tai-mui-hong",
    "thuoc/thuoc-than-kinh",
    "thuoc/thuoc-tiem-chich-and-dich-truyen",
    "thuoc/thuoc-tieu-hoa-and-gan-mat",
    "thuoc/thuoc-tim-mach-and-mau",
    "thuoc/thuoc-tiet-nieu-sinh-duc",
    "thuoc/thuoc-te-boi",
    "thuoc/thuoc-tri-tieu-duong"
]
try:
    with open("data.json","r",encoding="utf-8") as a:
        old=json.load(a)
except(FileNotFoundError):
    old={"products":[]}
for nhom in list:
    for j in range(0,900,10): 
        
        payload = {
            "skipCount":j,
            "maxResultCount": 10,
            "category": [nhom],
            "codes": [
                "productTypes", "priceRanges", "prescription", "objectUse", 
                "skin", "flavor", "manufactor", "indications", "brand", 
                "brandOrigin", "producer", "specification", "ingredient"
            ],
            "sortType": 4
        }

        re=requests.post(url=url,headers=headers,json=payload)
        datan=re.json()
        if not datan["products"]:
            break
        
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
        old["products"].extend(datan["products"])
        with open("data.json","w",encoding="utf-8") as b:
                json.dump(old,b,indent=4,ensure_ascii=False)


