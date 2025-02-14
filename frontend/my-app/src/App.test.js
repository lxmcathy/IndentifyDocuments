import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import App from './App';
import '@testing-library/jest-dom';

// Create Axios Mock
const mock = new MockAdapter(axios);

describe('App Component', () => {
  beforeEach(() => {
    // Reset Axios mock before each test
    mock.reset();
  });

  // Test 1: Render the upload button and file input
  it('renders the upload button and file input', () => {
    render(<App />);

    // Check if the upload button is rendered
    expect(screen.getByRole('button', { name: /Upload/i })).toBeInTheDocument();

    // Check if the file input is rendered
    expect(screen.getByLabelText(/Choose a file/i)).toBeInTheDocument();
  });

  // Test 2: Simulate file upload and verify the result
  it('allows file upload and displays the result', async () => {
    render(<App />);

    // Mock the upload API response
    mock.onPost('http://127.0.0.1:8000/upload/').reply(200, {
      filename: 'test.txt',
      predicted_category: 'General Article',
      confidence: 0.95,
    });

    // Simulate file selection
    const file = new File(['dummy content'], 'test.txt', { type: 'text/plain' });
    const fileInput = screen.getByLabelText(/Choose a file/i);
    fireEvent.change(fileInput, { target: { files: [file] } });

    // Simulate clicking the upload button
    const uploadButton = screen.getByRole('button', { name: /Upload/i });
    fireEvent.click(uploadButton);

    // Wait for the result to be displayed
    await waitFor(() => {
      expect(screen.getByText('Classification Result')).toBeInTheDocument();
      expect(screen.getByText('Filename: test.txt')).toBeInTheDocument();
      expect(screen.getByText('Predicted Category: General Article')).toBeInTheDocument();
      expect(screen.getByText('Confidence: 0.95')).toBeInTheDocument();
    });
  });

  // Test 3: Fetch and display document statistics
  it('fetches and displays document statistics', async () => {
    // Mock the statistics API responses
    mock.onGet('http://127.0.0.1:8000/statistics/document_distribution').reply(200, {
      categories: ['Technical Documentation', 'General Article'],
      counts: [5, 10],
    });

    mock.onGet('http://127.0.0.1:8000/statistics/upload_trends').reply(200, {
      trends: [/* mock data */],
    });

    mock.onGet('http://127.0.0.1:8000/statistics/confidence_distribution').reply(200, {
      distribution: [/* mock data */],
    });

    render(<App />);

    // Wait for the statistics to be displayed
    await waitFor(() => {
      expect(screen.getByText('Document Distribution by Type')).toBeInTheDocument();
      expect(screen.getByText('Technical Documentation: 5 documents')).toBeInTheDocument();
      expect(screen.getByText('General Article: 10 documents')).toBeInTheDocument();
    });
  });

  // Test 4: Fetch and display uploaded documents
  it('fetches and displays uploaded documents', async () => {
    // Mock the documents API response
    mock.onGet('http://127.0.0.1:8000/documents/').reply(200, [
      {
        filename: 'doc1.txt',
        predicted_category: 'Technical Documentation',
        confidence: 0.9,
        upload_time: '2023-10-01T12:00:00Z',
      },
      {
        filename: 'doc2.txt',
        predicted_category: 'General Article',
        confidence: 0.85,
        upload_time: '2023-10-02T12:00:00Z',
      },
    ]);

    render(<App />);

    // Wait for the documents to be displayed
    await waitFor(() => {
      expect(screen.getByText('Uploaded Documents')).toBeInTheDocument();
      expect(screen.getByText('doc1.txt')).toBeInTheDocument();
      expect(screen.getByText('doc2.txt')).toBeInTheDocument();
    });
  });

  // Test 5: Simulate sorting documents
  it('sorts documents by latest upload, category, and confidence', async () => {
    // Mock the documents API response
    mock.onGet('http://127.0.0.1:8000/documents/').reply(200, [
      {
        filename: 'doc1.txt',
        predicted_category: 'Technical Documentation',
        confidence: 0.9,
        upload_time: '2023-10-01T12:00:00Z',
      },
      {
        filename: 'doc2.txt',
        predicted_category: 'General Article',
        confidence: 0.85,
        upload_time: '2023-10-02T12:00:00Z',
      },
    ]);

    render(<App />);

    // Wait for the documents to be displayed
    await waitFor(() => {
      expect(screen.getByText('Uploaded Documents')).toBeInTheDocument();
    });

    // Sort by category
    const sortSelect = screen.getByLabelText(/Sort by/i);
    fireEvent.change(sortSelect, { target: { value: 'category' } });

    // Verify the sorted order
    await waitFor(() => {
      const documentItems = screen.getAllByRole('listitem');
      expect(documentItems[0]).toHaveTextContent('General Article');
      expect(documentItems[1]).toHaveTextContent('Technical Documentation');
    });

    // Sort by confidence
    fireEvent.change(sortSelect, { target: { value: 'confidence' } });

    // Verify the sorted order
    await waitFor(() => {
      const documentItems = screen.getAllByRole('listitem');
      expect(documentItems[0]).toHaveTextContent('Confidence: 0.9');
      expect(documentItems[1]).toHaveTextContent('Confidence: 0.85');
    });
  });
});