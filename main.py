from openai import OpenAI
from rapidocr_onnxruntime import RapidOCR
from elasticsearch import Elasticsearch
def ocr():
    engine = RapidOCR()
    image_path = "photo_6239982346425798374_y.jpg"
    result, elapse = engine(image_path)
    name = ""
    for line in result:
        box, text, score = line
        name += text + "\n"
    return name
def llm(text):
    client = OpenAI(
        base_url="http://localhost:3001/v1", 
        api_key="freellmapi-b7079f0480566e7a5a4f784cbd933a48d68bc2d0a211aac1" 
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[
        {
            "role": "user", 
            "content": (
                "Bạn là một chuyên gia y tế chuyên bóc tách dữ liệu OCR. Hãy tìm và chỉ in ra tên "
                "thương mại của thuốc từ đoạn văn bản sau. Nếu tên thuốc bị viết sai chính tả, mất dấu, "
                "hoặc dính chữ do lỗi quét OCR, hãy tự động sửa lại và chuẩn hóa về dạng tên thuốc đúng "
                "chính xác trên thực tế. Không bao gồm hoạt chất, không giải thích, không chào hỏi, "
                f"không thêm bất kỳ ký tự nào khác ngoài tên thuốc đã chuẩn hóa: {text}"
            
            )
        }
    ]
    )

    return response.choices[0].message.content
def search(name):
    es=Elasticsearch(["http://localhost:9200"])
    search= {
        "query": {
            "match": {
                "name": name
            }
        }
    }
    res=es.search(index="mediclist", body=search)
    hits=res['hits']['hits']
    if not hits:
        print("khong tim thay ket qua")
    kq=hits[0]['_source']
    print(f"MÃ THUỐC:{kq.get('sku')}")
    print(f"TÊN THUỐC: {kq.get('name')}")
    print(f"CÁCH DÙNG:\n {kq.get('usage_instructions')}")
    print(f"CÔNG DỤNG:\n {kq.get('description')}")
    if kq.get('price') is not None:
        print(f"giá: {kq.get('price')}")
if __name__ == "__main__":
    text=ocr()
    name=llm(text)
    search(name)