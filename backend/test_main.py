import pytest
from fastapi.testclient import TestClient
from database import insert_document, get_all_documents
import sys
import os
from main import app

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))  # 添加当前目录到 `sys.path`

client = TestClient(app)

# Test 1: File upload
def test_upload_txt_file():
    file_content = b"Sample text content"
    files = {"file": ("test.txt", file_content, "text/plain")}
    response = client.post("/upload/", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert "predicted_category" in data
    assert "confidence" in data

# Test 2: Invalid file upload
def test_upload_invalid_file():
    file_content = b"Invalid file"
    files = {"file": ("test.exe", file_content, "application/octet-stream")}
    response = client.post("/upload/", files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Only .txt, .pdf, and .docx files are supported"

# Test 3: Get all documents
def test_get_documents():
    response = client.get("/documents/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test 4: Get dociument distribution
def test_get_document_distribution():
    response = client.get("/statistics/document_distribution")
    assert response.status_code == 200
    assert "categories" in response.json()
    assert "counts" in response.json()

# Test 5: Get upload trends
def test_get_upload_trends():
    response = client.get("/statistics/upload_trends")
    assert response.status_code == 200
    assert "upload_times" in response.json()

# Test 6: Get confidence distribution
def test_get_confidence_distribution():
    response = client.get("/statistics/confidence_distribution")
    assert response.status_code == 200
    assert "confidence_scores" in response.json()
