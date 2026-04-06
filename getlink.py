import requests
import json
url="https://api.nhathuoclongchau.com.vn/lccus/search-product-service/api/products/ecom/product/search"
payload={
    "keyword": "panadol", "maxResultCount": 16, 
    "skipCount": 0, "sortType": 4
}
data=requests.post(url,json=payload)
res=data.json()
if data.status_code == 200:
    with open("data.json", "w", encoding="utf-8") as f:
            json.dump(res,f,indent=4,ensure_ascii=False)