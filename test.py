import os
import json
import re
import gc
from elasticsearch import Elasticsearch
from openai import OpenAI
from rapidocr_onnxruntime import RapidOCR
engine = RapidOCR()
ES = Elasticsearch(["http://localhost:9200"])
def llm(text):
    prompt = f"""Bạn là hệ thống trích xuất tên thuốc chuyên nghiệp từ văn bản OCR (bao gồm đơn thuốc, danh sách thuốc hoặc vỏ hộp).

NHIỆM VỤ:
Trích xuất tất cả các SẢN PHẨM THUỐC riêng biệt xuất hiện trong văn bản OCR, kèm hàm lượng.

QUY TẮC BẮT BUỘC:

1. LOẠI BỎ RÁC TRƯỚC KHI XÉT GHÉP SẢN PHẨM (thực hiện bước này đầu tiên):
   - Loại các cụm không phải tên thuốc, kể cả khi chúng đứng sát ngay cạnh một con số hàm lượng: nhãn "thuốc kê đơn"/Rx, quy cách đóng gói (hộp, vỉ, viên, nén, bao phim, chai, lọ, ống, gói + số lượng), cách dùng/liều dùng, tên bác sĩ, tên bệnh nhân, chữ ký, ngày tháng, tên nhà sản xuất/công ty đăng ký đứng riêng lẻ, văn bản pháp lý, số đăng ký (SĐK/SDK).
   - Văn bản OCR có thể bị mất dấu tiếng Việt và dính liền nhiều từ không có khoảng trắng (ví dụ "ThuocKeEon" = "Thuốc kê đơn", "Hop3vien10nenbaophim" = "Hộp 3 vỉ x 10 viên nén bao phim", "Bacsidieutri" = "Bác sĩ điều trị"). Phải nhận diện các cụm rác này dựa trên NGỮ NGHĨA khi đọc không dấu/dính liền, không chỉ so khớp chuỗi có dấu và có khoảng trắng.
   - Một chuỗi ký tự đứng gần hàm lượng KHÔNG mặc nhiên là tên thuốc. Chỉ coi là tên thuốc nếu bản chất của nó là tên riêng (tên biệt dược/thương hiệu, hoặc tên hoạt chất dạng khoa học) — không phải cụm mô tả đóng gói, liều dùng, hay nhãn pháp lý/hành chính.

2. XÁC ĐỊNH RANH GIỚI SẢN PHẨM (chỉ áp dụng cho các cụm đã qua bước lọc ở trên):
   - Một sản phẩm thuốc thường có tới 2 loại tên đi kèm nhau: tên biệt dược (thương hiệu, thường viết hoa/in đậm) và tên hoạt chất (INN, dạng khoa học, có thể kèm chú thích "dưới dạng ..."). Đây là HAI CÁCH GỌI CHO CÙNG MỘT SẢN PHẨM, không phải hai sản phẩm.
   - Coi hai tên là CÙNG một sản phẩm khi có ít nhất một trong các dấu hiệu sau: (a) chúng đi kèm cùng một con số hàm lượng, (b) hàm lượng chỉ xuất hiện một lần trong khu vực văn bản đó nhưng có nhiều tên thuốc nằm gần nó, (c) một tên là chú thích/diễn giải của tên kia (ví dụ dạng "(dưới dạng ...)" hoặc đặt trong ngoặc ngay sau tên hoạt chất).
   - Hoạt chất hoặc hàm lượng có thể bị in lặp lại nhiều lần trên bao bì thật (mặt trước/mặt sau, nhiều ngôn ngữ, nhiều cỡ chữ). Lặp lại như vậy KHÔNG được tính là sản phẩm thứ hai — chỉ tạo thêm phần tử JSON mới khi xuất hiện một hàm lượng số khác hoặc một tên thuốc rõ ràng không liên quan đến sản phẩm đã ghi nhận.

2b. THUỐC PHỐI HỢP NHIỀU HOẠT CHẤT (mỗi hoạt chất có hàm lượng riêng):
   - Khi một cụm thuốc liệt kê từ 2 hoạt chất trở lên nối bằng "+" và đi kèm từng ấy con số hàm lượng tương ứng theo đúng thứ tự (ví dụ "A + B ... x mg + y mg"), đây vẫn là MỘT sản phẩm phối hợp duy nhất — không tách thành nhiều phần tử theo số lượng hàm lượng có mặt.
   - Định dạng riêng cho trường hợp này: "<Tên biệt dược nếu có> (<Hoạt chất 1> <Hàm lượng 1> + <Hoạt chất 2> <Hàm lượng 2>)". Nếu không có tên biệt dược, dùng "<Hoạt chất 1> <Hàm lượng 1> + <Hoạt chất 2> <Hàm lượng 2>".

3. ĐỊNH DẠNG MỖI SẢN PHẨM (áp dụng cho sản phẩm một hoạt chất, không thuộc trường hợp 2b):
   - Nếu một sản phẩm có cả tên biệt dược và tên hoạt chất: dùng "<Tên biệt dược> <Hàm lượng> (<Tên hoạt chất>)".
   - Nếu chỉ có một tên (chỉ biệt dược HOẶC chỉ hoạt chất): dùng "<Tên đó> <Hàm lượng>".
   - Mỗi sản phẩm chỉ xuất hiện đúng MỘT LẦN trong mảng kết quả, dù tên hoặc hàm lượng của nó có bị lặp lại bao nhiêu lần trong văn bản gốc.

4. ĐẦU RA BẮT BUỘC:
   - Trả về duy nhất 1 JSON array chứa danh sách các chuỗi tên thuốc đã lọc sạch, mỗi sản phẩm một phần tử duy nhất.
   - Tuyệt đối không thêm markdown, không dùng code fence, không giải thích hay thêm bất kỳ chữ nào ngoài JSON.

VĂN BẢN OCR:
\"\"\"
{text}
\"\"\""""

    client = OpenAI(
        base_url="http://localhost:3001/v1",
        api_key="freellmapi-9dc4980c9e0c1101dac6211702e9e2ce34b0bfb4e1336ada",
    )

    response = client.chat.completions.create(
        model="auto",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
def ocr(ds):
    all_candidates = []
    for idx, anh in enumerate(ds, start=1):
        kq, tg = engine(anh)
        ten = ""
        if kq:
            for line in kq:
                toado, chu, diem = line
                ten += chu + "\n"

        frm = llm(ten)
        clean = frm.replace("```json", "").replace("```", "").strip()

        try:
            frag = json.loads(clean)
        except json.JSONDecodeError:
            print(f"anh {idx} ({anh}) llm tra ve khong phai json, bo qua:", clean[:200])
            continue

        candidates = []
        if isinstance(frag, list):
            for i in frag:
                strin = str(i).strip()
                if strin:
                    candidates.append(strin)
        elif isinstance(frag, str) and frag.strip():
            candidates.append(frag.strip())
        if candidates:
            all_candidates.append(candidates)
        print(ten)
        del kq, tg

    gc.collect()
    return all_candidates
def searchh(name):
    search = {
        "size": 1,
        "query": {
            "multi_match": {
                "query": name,
                "fields": ["name^2", "ingredients"],
                "fuzziness": "AUTO"
            }
        }
    }
    res = ES.search(index="danh_sach_thuoc", body=search)
    hits = res['hits']['hits']
    
    if not hits:
        print(f"khong tim thay ket qua cho: {name}")
        return None

    kq = hits[0]['_source']
    result = f"MÃ THUỐC: {kq.get('sku')}\n"
    result += f"TÊN THUỐC: {kq.get('name')}\n"
    result += f"HOẠT CHẤT: {kq.get('ingredients')}\n"
    result += f"CÁCH DÙNG:\n {kq.get('usage_instructions')}\n"
    result += f"CÔNG DỤNG:\n {kq.get('description')}\n"
    if kq.get('price') is not None:
        result += f"GIÁ: {kq.get('price')}\n"

    return result, kq.get('name'), kq.get('ingredients')
def make_clean(text):
    if not text:
        return []
    raw_items = re.split(r'[,+]', text)

    clean = []
    for item in raw_items:
        words = item.strip().split()
        if words:
            first = words[0].strip()
            if len(first) > 2:
                clean.append(first)
    return clean
def interaction(name1, name2):
    n1 = name1.lower().strip()
    n2 = name2.lower().strip()
    if n1.endswith('e'):
        n1 = n1[:-1]
    if n2.endswith('e'):
        n2 = n2[:-1]

    search = {
        "size": 1,
        "query": {
            "bool": {
                "should": [
                    {
                        "bool": {
                            "must": [
                                {"match": {"các_thuốc_trong_nhóm": {"query": n1, "operator": "and", "fuzziness": "AUTO"}}},
                                {"match": {"thuốc_tương_tác": {"query": n2, "operator": "and", "fuzziness": "AUTO"}}}
                            ]
                        }
                    },
                    {
                        "bool": {
                            "must": [
                                {"match": {"các_thuốc_trong_nhóm": {"query": n2, "operator": "and", "fuzziness": "AUTO"}}},
                                {"match": {"thuốc_tương_tác": {"query": n1, "operator": "and", "fuzziness": "AUTO"}}}
                            ]
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }
    }

    res = ES.search(index="tuong_tac_thuoc", body=search)
    hit = res["hits"]["hits"]

    if not hit:
        return f"an toan: {name1} - {name2}\n"

    kq = hit[0]["_source"]
    resu = f"\n--- CÓ TƯƠNG TÁC: {name1.upper()} - {name2.upper()} ---\n"
    resu += f"Phân tích tương tác: {kq.get('phân_tích_tương_tác')}\n"
    resu += f"Xử lý tương tác: {kq.get('xử_lý_tương_tác')}\n"
    return resu
if __name__ == "__main__":
    ds = ['photo_6249090773764740410_y.jpg']
    names = ocr(ds) 
    
    with open('daxl.json', 'w', encoding='utf-8') as f:
        json.dump(names, f, ensure_ascii=False, indent=4)
        
    with open('daxl.json', 'r', encoding="utf-8") as f:
        data = json.load(f)
        
    drug = []
    infor = ''
    interac = ''
    
    # Loop qua từng ảnh trong data
    for candidates in data:
        # Loop qua TỪNG THUỐC thu được trong ảnh đó
        for single_drug in candidates:
            res = searchh(single_drug)
            if res:
                kq_text, full_name, ingredients = res
                infor += kq_text + "\n" + "_" * 40 + "\n"
                target_raw = ingredients if ingredients else full_name
                cleaned_ings = make_clean(target_raw)
                drug.extend(cleaned_ings)

    drug = list(set(drug))
    for i in range(len(drug)):
        for j in range(i + 1, len(drug)):
            tuongtac = interaction(drug[i], drug[j])
            if tuongtac:
                interac += tuongtac
                
    last = infor + interac if interac else infor
    with open("ketqua.txt", "w", encoding="utf-8") as f:
        f.write(last)
    print("da luu ketqua.txt")