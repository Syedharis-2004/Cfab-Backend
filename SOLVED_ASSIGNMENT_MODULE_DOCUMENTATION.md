# Solved Assignment System - Module Documentation

This module provides automated tools for students to solve PDF-based assignments and generate data visualization recommendations using AI.

## Module Overview
The Solved Assignment System is designed to handle complex datasets and PDF questions. It uses the Google Gemini 2.5 Flash model for intelligent data analysis and decision-making.

---

## 1. Python Mode (AI Data Analyst)
**Endpoint**: `POST /api/solved-assignment/process-python`

### Purpose
Automatically extracts questions from a PDF, analyzes a provided dataset (CSV/Excel), and generates a completed response file with answers.

### Input Parameters (Multipart/Form-Data)
- `pdf_file`: The assignment question paper (PDF).
- `dataset_file`: The raw data source (CSV or XLSX).
- `response_file`: The template file to be filled (CSV or XLSX).

### Processing Flow
1. **Validation**: Checks file extensions and sizes.
2. **PDF Extraction**: Uses `pdfplumber` to extract clean text and detect questions.
3. **Dataset Analysis**: Loads data into Pandas, cleans missing values, and generates a context summary for the AI.
4. **AI Processing**: Sends context + questions to Gemini 2.5 Flash.
5. **Response Filling**: Inserts AI-generated answers into the uploaded response template.
6. **Summary Generation**: Creates a `summary.txt` with processing metadata.
7. **History Tracking**: Stores the activity, file paths, and status in MongoDB.

### Expected Response
```json
{
  "success": true,
  "response_file": "path/to/solved_assignment.xlsx",
  "summary_file": "path/to/summary.txt",
  "questions_processed": 10
}
```

---

## 2. Power BI Mode (Visualization Assistant)
**Endpoint**: `POST /api/solved-assignment/process-powerbi`

### Purpose
Analyzes dataset columns and assignment questions to recommend the most effective Power BI visualizations.

### Input Parameters (Multipart/Form-Data)
- `pdf_file`: The assignment questions (PDF).
- `dataset_file`: The dataset to be visualized (CSV or XLSX).

### Processing Flow
1. **Extraction**: Detects questions from the PDF.
2. **Mapping**: Matches questions to dataset columns intelligently.
3. **Recommendation**: Gemini suggests the best visual type (Bar Chart, Pie Chart, Line Chart, etc.).
4. **Config Generation**: Creates a `visualization_config.json` containing the recommended visual mapping.
5. **History Tracking**: Saves the session details to MongoDB.

### Expected Response
```json
{
  "success": true,
  "config_file": "path/to/visualization_config.json",
  "visuals_generated": 8
}
```

---

## File Storage Structure
All generated outputs are stored in a structured manner:
`outputs/{user_id}/{assignment_id}/`

- `solved_filename.xlsx`: The final completed assignment.
- `summary.txt`: Metadata about the processing run.
- `visualization_config.json`: The config for Power BI.
- `original_files...`: The originally uploaded files are kept for reference.

## Error Handling
The module returns descriptive errors for:
- Invalid file formats (Supported: PDF, CSV, XLSX).
- Empty or corrupted PDFs.
- Missing columns or data in the dataset.
- AI processing timeouts or failures.
