from elasticsearch import Elasticsearch

es=Elasticsearch(["http://localhost:9200"])
search={
    "query": {
        "match": {
            "name":{
                "query": "Viên nén Onglyza",
                "fuzziness": "AUTO"
            }
        }
    },
    "size":1
}
res=es.search(index="mediclist", body=search)
hits=res['hits']['hits']
if not hits:
    print("khong tim thay ket qua")
kq=hits[0]['_source']
print(f"ma thuoc:{kq.get('id')}")
print(f"ten thuoc: {kq.get('name')}")
print(f"cong dung: {kq.get('description')}")