from google import genai
import os
from dotenv import load_dotenv
import json
load_dotenv()
api_key = os.getenv("api")
client = genai.Client(api_key=api_key)
file=client.files.upload(file="DSC_099842_74c1fc532a.webp")
prompt="""
analyze this medicine box image. Extract the following information. Structure the output as a clean JSON object.
Desired Fields:
Name: The primary commercial name.
Total_Count: The number of pills/tablets in the box;
Return only the JSON string, without any additional explanations."""
res=client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents=[prompt,file]
)
jso=res.text.replace("```json", "").replace("```", "").strip()

data = json.loads(jso)
with open("tenthuoc.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)