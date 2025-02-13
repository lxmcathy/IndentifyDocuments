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

# Load zero-shot classification model
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Dedine categories
CATEGORIES = [
    "Technical Documentation",
    "Business Proposal",
    "Legal Document",
    "Academic Paper",
    "General Article",
    "Other"
]

CONFIDENCE_THRESHOLD = 0.3  # Threshold for low confidence warning
LOW_CONFIDENCE_THRESHOLD = 0.2  # # Threshold for classifying as "Other"
CHUNK_SIZE = 512  # Size of text chunks for processing

# Pydantic model for document response
class DocumentResponse(BaseModel):
    filename: str
    predicted_category: str
    confidence: float
    upload_time: datetime.datetime

# Extract PDF
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Extract DOC/DOCX
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

def chunk_text(text, chunk_size=512):
    """Split text into chunks, each with a maximum length of chunk_size"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


# Endpoint to upload documents
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

    chunks = chunk_text(content)

    # Classify each chunk
    results = [classifier(chunk, CATEGORIES) for chunk in chunks]

    # Select the classification with the highest confidence
    best_result = max(results, key=lambda r: r["scores"][0])
    predicted_category = best_result["labels"][0]
    confidence = best_result["scores"][0]


    result = classifier(content, CATEGORIES)
    predicted_category = result["labels"][0]
    confidence = result["scores"][0]

    warning = None
    if confidence < CONFIDENCE_THRESHOLD:
        warning = f"Warning: The confidence score ({confidence:.2f}) is low, the prediction may not be accurate."
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        redicted_category = "Other"


    insert_document(file.filename, predicted_category, confidence, datetime.datetime.now().isoformat())

    return {
        "filename": file.filename,
        "predicted_category": predicted_category,
        "confidence": confidence,
        "upload_time": datetime.datetime.now().isoformat(),
        "warning": warning
    }

# Endpoint to retrieve list of documents
@app.get("/documents/", response_model=List[DocumentResponse])
async def get_documents():
    documents = get_all_documents()
    if not documents:
        raise HTTPException(status_code=404, detail="No documents found")
    
    return [DocumentResponse(**doc) for doc in documents]


# Endpoint to get document category distribution
@app.get("/statistics/document_distribution")
async def document_distribution():
    data = get_document_distribution()
    return {"categories": data['categories'], "counts": data['counts']}

# Endpoint to get upload trends
@app.get("/statistics/upload_trends")
async def upload_trends():
    data = get_upload_trends()
    return {"upload_times": data}

# Endpoint to get confidence distribution
@app.get("/statistics/confidence_distribution")
async def confidence_distribution():
    data = get_confidence_distribution()
    return {"confidence_scores": data}

#Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
