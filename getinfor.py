import requests
from bs4 import BeautifulSoup

url = "https://nhathuoclongchau.com.vn/thuoc/fucagi-500-mg-agimexpharm-1-v.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


res = requests.get(url,headers=headers)

if res.status_code == 200:
    html = BeautifulSoup(res.content, "html.parser")
    
    with open("information.txt", "w", encoding="utf-8") as f:
        kq = html.find("div", class_="usage")
        if kq:
            f.write("--- MÔ TẢ SẢN PHẨM ---\n")
            mota_text = kq.get_text(separator='\n', strip=True)
            f.write(mota_text + "\n\n")
        ue = html.find("div", class_="dosage")
        if ue:
            f.write("--- HƯỚNG DẪN SỬ DỤNG ---\n")
            huong_dan_text = ue.get_text(separator='\n', strip=True)
            f.write(huong_dan_text)
else:
    print(f"Mã lỗi: {res.status_code}")