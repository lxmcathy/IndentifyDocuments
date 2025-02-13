# Document Classification Application

## Overview

This application allows users to upload documents, classify their content using a pre-trained machine learning model, and view the results in a clean and user-friendly web interface. The application supports plain text files, PDFs, and DOC/DOCX formats. It uses the facebook/bart-large-mnli model from the Hugging Face Transformers library for zero-shot classification. The classified documents are stored in a SQLite database, and the application provides a RESTful API for document upload and retrieval.

## Setup

### Backend
1. Navigate to the `backend` folder:
   ```bash
   cd backend

2. Install dependencies:
    pip install -r requirements.txt

3. Run the Fast API server:
    uvicorn main:app --reload

### Frontend
1. Navigate to the frontend folder:
    cd frontend
2. Install dependencies:
    npm install
3. Run the React app:
    npm start

## Core Functionality

### Document Upload
1. Users can upload/drag documents through a web interface.
2. Supported file formats: `.txt`, `.pdf`, `.doc`, and `.docx`.
3. The application extracts text content from the uploaded documents.

### Document Classification
1. Documents are classified into one of the following categories:
  - Technical Documentation
  - Business Proposal
  - Legal Document
  - Academic Paper
  - General Article
  - Other
2. The predicted category and confidence score are displayed for each uploaded document.

### Results Display and User Interface
1. A clean and user-friendly web UI allows users to:
  - Upload documents (drag-and-drop supported).
  - View classification results, including the predicted category and confidence score.
  - Browse a list of previously uploaded documents with key information (filename, predicted category, confidence, and upload time).

### Data Storage
Uploaded document metadata (filename, predicted category, confidence, and upload timestamp) is stored in a SQLite database.

### API Design
1. The application provides a RESTful API for document upload and retrieval of classification results.
2. Key endpoints:
  - `POST /upload/`: Upload a document for classification.
  - `GET /documents/`: Retrieve a list of all uploaded documents.
  - `GET /statistics/document_distribution`: Retrieve document distribution by type.
  - `GET /statistics/upload_trends`: Retrieve upload trends over time.
  - `GET /statistics/confidence_distribution`: Retrieve confidence score distribution.

### Statistics
1. The application includes a simple statistics dashboard that displays:
  - Document distribution by type.
  - Upload trends over time.
  - Confidence score distribution.

### Error Handling
1. The application includes robust error handling for:
 - Invalid file types.
 - Corrupt files.
 - API and database errors.
2. Informative error messages are provided in both API responses and the UI.

## Evaluation Criteria
1. Functionality
 - The application meets all core requirements, including document upload, classification, and result display.
 2. Code Quality
 - The code is clean, well-structured, and well-commented.
 - Robust error handling is implemented throughout the application.
 3. Backend Implementation
 - The API is well-designed, RESTful, and documented.
 - Data validation is implemented using Pydantic.
 - Error responses are meaningful and informative.
 4. Going the Extra Mile
 - The application includes a simple statistics dashboard.

 ###Deliveries
 Respository: https://github.com/lxmcathy/IndentifyDocuments.git