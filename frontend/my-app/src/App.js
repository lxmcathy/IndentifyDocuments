import React, { useState, useCallback, useRef, useEffect } from "react";
import axios from "axios";
import { useDropzone } from "react-dropzone";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [documents, setDocuments] = useState([]);
  const fileInputRef = useRef(null);
  const [visibleCount, setVisibleCount] = useState(5);
  const [sortBy, setSortBy] = useState("latest");
  const [statistics, setStatistics] = useState({
    documentDistribution: null,
    uploadTrends: null,
    confidenceDistribution: null,
  });

  // Handle file drop using react-dropzone
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0];
      console.log("Selected file:", selectedFile);
      setFile(selectedFile);
    }
  }, []);

  // Configure react-dropzone
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    accept: {
      "text/plain": [".txt"],
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
  });

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      console.log("Selected file manually:", selectedFile);
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:8000/upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      console.log("Upload response:", response.data);
      setResult(response.data);

      // Add the new document to the front of the list
      setDocuments((prevDocs) => [
        {
          filename: response.data.filename,
          predicted_category: response.data.predicted_category,
          confidence: response.data.confidence,
          upload_time: new Date().toISOString(),
        },
        ...prevDocs,
      ]);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert(error.response?.data?.detail || "Failed to upload file. Please try again.");
    }
  };

  //Fetch the list of uploaded documents from the backend
  const fetchDocuments = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/documents/");
      console.log("Fetched documents:", response.data);

      const sortedDocs = response.data
        .filter((doc) => doc.upload_time)
        .map((doc) => ({
          ...doc,
          upload_time: new Date(doc.upload_time).toISOString(),
        }))
        .sort((a, b) => new Date(b.upload_time) - new Date(a.upload_time));

      setDocuments(sortedDocs);
    } catch (error) {
      console.error("Error fetching documents:", error);
      console.log(error.response ? error.response.data : error.message);
    }
  };

  // Fetch statistics from the backend
  const fetchStatistics = async () => {
    try {
      const documentDistribution = await axios.get("http://127.0.0.1:8000/statistics/document_distribution");
      const uploadTrends = await axios.get("http://127.0.0.1:8000/statistics/upload_trends");
      const confidenceDistribution = await axios.get("http://127.0.0.1:8000/statistics/confidence_distribution");

      console.log("Upload Trends:", uploadTrends.data); // Check the structure of the data
      console.log("Confidence Distribution:", confidenceDistribution.data); // Check the structure of the data

      setStatistics({
        documentDistribution: documentDistribution.data,
        uploadTrends: uploadTrends.data,
        confidenceDistribution: confidenceDistribution.data,
      });
    } catch (error) {
      console.error("Error fetching statistics:", error);
    }
  };

  // Fetch documents and statistics on component mount
  useEffect(() => {
    fetchDocuments();
    fetchStatistics();
  }, []);

  const loadMore = () => {
    setVisibleCount((prev) => prev + 10);
  };

  const sortedDocuments = [...documents].sort((a, b) => {
    if (sortBy === "latest") {
      return new Date(b.upload_time) - new Date(a.upload_time);
    } else if (sortBy === "category") {
      return a.predicted_category.localeCompare(b.predicted_category);
    } else if (sortBy === "confidence") {
      return b.confidence - a.confidence;
    }
    return 0;
  });

  return (
    <div className="App">
      <header className="App-header">
        <h1>Identify your Documents</h1>

        {/* Drag-and-drop upload area */}
        <div {...getRootProps()} className="dropzone">
          <input {...getInputProps()} />
          {file ? <p>Selected file: {file.name}</p> : isDragActive ? <p>Drop the file here...</p> : <p>Drag your file here or click to select a file</p>}
        </div>

        <div className="upload-section">
          <label htmlFor="file-upload">Choose a file:</label>
          <input
            type="file"
            id="file-upload"
            onChange={handleFileChange}
            ref={fileInputRef} 
            aria-label="Upload"
          />
          <button onClick={handleUpload}>Upload</button>
        </div>
      </header>

      {result && (
        <div className="result-section">
          <h2>Classification Result</h2>
          <p>Filename: {result.filename}</p>
          <p>Predicted Category: {result.predicted_category}</p>
          <p>Confidence: {result.confidence}</p>
        </div>
      )}

      <div className="document-list">
        <h2>Uploaded Documents</h2>
        <div>
          <label>Sort by: </label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="latest">Latest Upload</option>
            <option value="category">Top Predicted Category</option>
            <option value="confidence">Highest Confidence Score</option>
          </select>
        </div>

        <ul>
          {sortedDocuments.slice(0, visibleCount).map((doc, index) => (
            <li key={index}>
              <strong>{doc.filename}</strong> - {doc.predicted_category} (Confidence: {doc.confidence})<br />
              <small>Uploaded: {new Date(doc.upload_time).toLocaleString()}</small>
            </li>
          ))}
        </ul>

        {visibleCount < documents.length && <button onClick={loadMore}>Load More</button>}
      </div>

      {/* Statistics Dashboard */}
      <div className="statistics-dashboard">
        <h2>Statistics Dashboard</h2>

        {/* Document category distribution */}
        <div className="statistics-section">
          <h3>Document Distribution by Type</h3>
          {statistics.documentDistribution && (
            <ul>
              {statistics.documentDistribution.categories.map((category, index) => (
                <li key={category}>
                  {category}: {statistics.documentDistribution.counts[index]} documents
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Confidence distribution */}
        <div className="statistics-section">
          <h3>Upload Trends</h3>
          {statistics.uploadTrends && (
            <ul>
              {Object.entries(statistics.uploadTrends.upload_times).map(([date, count]) => (
                <li key={date}>
                  {date}: {count} documents
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Confidence Distribution */}
        <div className="statistics-section">
        <h3>Confidence Distribution</h3>
          {statistics.confidenceDistribution && (
            <ul>
              <li>Very High Confidence (≥ 0.8): {statistics.confidenceDistribution.confidence_scores.filter(score => score >= 0.8).length} documents</li>
              <li>High Confidence (0.6 - 0.8): {statistics.confidenceDistribution.confidence_scores.filter(score => score >= 0.6 && score < 0.8).length} documents</li>
              <li>Medium Confidence (0.4 - 0.6): {statistics.confidenceDistribution.confidence_scores.filter(score => score >= 0.4 && score < 0.6).length} documents</li>
              <li>Low Confidence (0.2 - 0.4): {statistics.confidenceDistribution.confidence_scores.filter(score => score >= 0.2 && score < 0.4).length} documents</li>
              <li>Very Low Confidence (&lt; 0.2): {statistics.confidenceDistribution.confidence_scores.filter(score => score < 0.2).length} documents</li>
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
