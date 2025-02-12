from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
import datetime
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from docx import Document
import tempfile
import os
from database import insert_document, get_all_documents,  get_all_documents, get_document_distribution, get_upload_trends, get_confidence_distribution

app = FastAPI()

# 加载零样本分类模型
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# 定义类别
CATEGORIES = [
    "Technical Documentation",
    "Business Proposal",
    "Legal Document",
    "Academic Paper",
    "General Article",
    "Other"
]

# Pydantic 模型
class DocumentResponse(BaseModel):
    filename: str
    predicted_category: str
    confidence: float
    upload_time: datetime.datetime

# 解析 PDF
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# 解析 DOC/DOCX
def extract_text_from_doc(file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(file.file.read())
            temp_file_path = temp_file.name
        
        doc = Document(temp_file_path)
        text = "\n".join([p.text for p in doc.paragraphs])

        os.remove(temp_file_path)
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing DOCX file: {str(e)}")

# 上传文件接口
@app.post("/upload/", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    if not (file.filename.endswith(".txt") or file.filename.endswith(".pdf") or file.filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Only .txt, .pdf, and .docx files are supported")

    try:
        if file.filename.endswith(".txt"):
            content = await file.read()
            content = content.decode("utf-8")
        elif file.filename.endswith(".pdf"):
            content = extract_text_from_pdf(file.file)
        elif file.filename.endswith(".doc") or file.filename.endswith(".docx"):
            content = extract_text_from_doc(file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

    result = classifier(content, CATEGORIES)
    predicted_category = result["labels"][0]
    confidence = result["scores"][0]

    # 创建目录如果不存在
    file_location = f"files/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)  # 确保 'files' 目录存在

    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())  # 保存文件到本地


    insert_document(file.filename, predicted_category, confidence, datetime.datetime.now().isoformat())

    return {
        "filename": file.filename,
        "predicted_category": predicted_category,
        "confidence": confidence,
        "upload_time": datetime.datetime.now().isoformat()
    }

# 获取文件列表接口
@app.get("/documents/", response_model=List[DocumentResponse])
async def get_documents():
    documents = get_all_documents()
    return [DocumentResponse(**doc) for doc in documents]


# 获取文档类别分布
@app.get("/statistics/document_distribution")
async def document_distribution():
    data = get_document_distribution()
    return {"categories": data['categories'], "counts": data['counts']}

# 获取上传趋势
@app.get("/statistics/upload_trends")
async def upload_trends():
    data = get_upload_trends()
    return {"upload_times": data}

# 获取置信度分布
@app.get("/statistics/confidence_distribution")
async def confidence_distribution():
    data = get_confidence_distribution()
    return {"confidence_scores": data}

# 允许 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
