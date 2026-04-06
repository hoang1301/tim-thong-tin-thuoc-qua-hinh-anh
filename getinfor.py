import requests
from bs4 import BeautifulSoup
url="https://nhathuoclongchau.com.vn/thuoc/panadol-extra-do-500mg-180v-sanofi-16965.html"
res=requests.get(url)
if res.status_code==200:
        with open("information.txt","w",encoding="utf-8") as f:
            html=BeautifulSoup(res.content,"html.parser")
            kq=html.find("div",class_="description")
            mota=kq.find_all("li")
            f.write("--- MÔ TẢ SẢN PHẨM ---\n")
            for mt in mota:
                re=mt.text.strip()
                f.write(re)
                f.write("\n")
           

            ue=html.find("div",class_="dosage")
            dir=ue.find_all(["h3","p","ul"])
            f.write("--- HƯỚNG DẪN SỬ DỤNG ---\n")
            for num in dir:
                f.write(num.text.strip())
                f.write("\n")

