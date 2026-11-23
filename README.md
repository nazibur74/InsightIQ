# InsightIQ

**AI-Powered Automated Data Analytics Platform**

InsightIQ is a web-based data analytics tool that helps users understand
spreadsheet data without having to perform every analysis manually.
Upload a CSV or Excel file to generate dataset profiles, data-quality
checks, business diagnostics, interactive analytics, anomaly detection,
forecasts, AI-assisted insights, and a downloadable PDF report.

------------------------------------------------------------------------

## Features

-   **CSV and Excel upload** --- supports `.csv`, `.xlsx`, and `.xls`
    files.
-   **Dataset profiling** --- summarizes rows, columns, data types,
    missing values, unique values, and other column-level information.
-   **Data quality analysis** --- identifies missing values, duplicate
    rows, blank values, inconsistent categories, numeric-looking text,
    constant columns, infinite values, and potentially invalid dates.
-   **Business diagnostics** --- uses dataset and column characteristics
    to identify relevant business observations.
-   **Interactive analytics dashboard** --- displays key metrics,
    time-based trends, category comparisons, and numeric summaries.
-   **Dashboard filters** --- filter analytics by date range and
    category when the uploaded data supports those fields.
-   **AI-powered Q&A** --- ask questions about the uploaded dataset
    using Google Gemini.
-   **Anomaly detection** --- uses statistical and machine-learning
    methods to flag unusual observations.
-   **Predictive analytics** --- generates time-series forecasts when
    sufficient dated data is available.
-   **AI predictive insights** --- produces natural-language
    explanations of forecast results.
-   **PDF report export** --- generates a report containing the
    available analysis results and visualizations.
-   **Analysis history** --- stores and displays saved dataset and
    analysis records using PostgreSQL.

> Forecasting and anomaly-detection results depend on the structure,
> quality, and size of the uploaded dataset. Some methods may report
> insufficient data when the dataset does not meet their requirements.

------------------------------------------------------------------------

## Technology Stack

### Frontend

-   React
-   Vite
-   Tailwind CSS
-   Recharts
-   Axios
-   Lucide React

### Backend

-   Python
-   FastAPI
-   Pandas
-   NumPy
-   SciPy
-   Scikit-learn
-   Statsmodels
-   Google GenAI SDK (Gemini)
-   SQLAlchemy
-   PostgreSQL
-   ReportLab
-   OpenPyXL

------------------------------------------------------------------------

## Project Structure

The project is organized into a frontend and backend. The following is a
high-level overview; individual filenames may differ in your local
project.

``` text
InsightIQ/
├── backend/
│   └── app/
│       ├── api/
│       │   ├── upload.py
│       │   └── history.py
│       ├── services/
│       │   ├── data_quality_service.py
│       │   ├── business_diagnostic_service.py
│       │   ├── analytics_service.py
│       │   ├── gemini_service.py
│       │   └── report_service.py
│       ├── database.py
│       ├── models.py
│       └── main.py
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── AIChat.jsx
│       │   ├── AnalysisHistory.jsx
│       │   ├── AnalyticsDashboard.jsx
│       │   ├── BusinessDiagnostics.jsx
│       │   ├── FileUploader.jsx
│       │   ├── PredictiveDashboard.jsx
│       │   └── QualityReport.jsx
│       ├── services/
│       │   └── api.js
│       ├── App.css
│       ├── App.jsx
│       ├── index.css
│       └── main.jsx
├── .gitignore
└── README.md
```

------------------------------------------------------------------------

## Requirements

Install the following before running the project:

-   Python 3.10 or newer (use the version supported by your installed
    dependencies)
-   Node.js and npm
-   PostgreSQL
-   A Google Gemini API key for AI-powered features

------------------------------------------------------------------------

## Setup and Installation

### 1. Clone the repository

``` bash
git clone https://github.com/YOUR_USERNAME/InsightIQ.git
cd InsightIQ
```

Replace `YOUR_USERNAME` with the GitHub account and repository URL where
you publish the project.

### 2. Configure the backend

Open a terminal in the backend directory:

``` bash
cd backend
```

Create and activate a virtual environment:

``` bash
python -m venv venv
```

Windows PowerShell:

``` powershell
.\venv\Scripts\Activate.ps1
```

Install the backend dependencies:

``` bash
pip install -r requirements.txt
```

If your project does not yet contain a `requirements.txt`, create one
from the working environment:

``` bash
pip freeze > requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the backend directory. Add your own credentials:

``` env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/InsightIQ_db
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

-   Create the `InsightIQ_db` database in PostgreSQL before starting the
    backend.
-   Use the environment-variable names expected by your application.
-   Never commit `.env` or publish API keys, database passwords, or
    other secrets.

### 4. Start the backend

From the backend directory, run the FastAPI application. For the common
`app.main:app` layout:

``` bash
uvicorn app.main:app --reload
```

The API should be available at:

``` text
http://127.0.0.1:8000
```

FastAPI interactive API documentation:

``` text
http://127.0.0.1:8000/docs
```

If your application entry point differs, adjust the Uvicorn module path
accordingly.

### 5. Configure and start the frontend

Open another terminal:

``` bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, commonly:

``` text
http://localhost:5173
```

The frontend API client is currently configured to use:

``` text
http://127.0.0.1:8000/api
```

Change the API base URL if your backend runs elsewhere.

------------------------------------------------------------------------

## How to Use

1.  Start PostgreSQL and the backend API.
2.  Start the React frontend.
3.  Open InsightIQ in your browser.
4.  Upload a CSV or Excel dataset.
5.  Review the dataset overview and column profiles.
6.  Explore data-quality results and business diagnostics.
7.  Use the analytics dashboard and available filters.
8.  Review anomaly detection and forecasting results.
9.  Ask questions about the dataset using the AI assistant.
10. Generate and download the PDF analysis report.
11. Open Analysis History to view saved analysis records.

------------------------------------------------------------------------

## API Overview

The backend currently includes the following API operations:

  --------------------------------------------------------------------------------------
  Method                  Endpoint                               Purpose
  ----------------------- -------------------------------------- -----------------------
  `POST`                  `/api/upload`                          Upload and analyze a
                                                                 dataset

  `POST`                  `/api/analytics/filter`                Recalculate analytics
                                                                 using filters

  `POST`                  `/api/ai/ask`                          Ask a question about an
                                                                 uploaded dataset

  `POST`                  `/api/ai/predictive-insights`          Generate AI
                                                                 explanations for
                                                                 predictive results

  `POST`                  `/api/reports/pdf`                     Generate a PDF analysis
                                                                 report

  `GET`                   `/api/history`                         List saved analysis
                                                                 history

  `GET`                   `/api/history/{dataset_id}`            Retrieve dataset
                                                                 details

  `GET`                   `/api/history/{dataset_id}/analysis`   Retrieve a saved
                                                                 analysis

  `DELETE`                `/api/history/{dataset_id}`            Delete a dataset and
                                                                 its related history

  `GET`                   `/api/health/database`                 Check the database
                                                                 connection
  --------------------------------------------------------------------------------------

All routes are subject to the backend's configured router prefixes.

------------------------------------------------------------------------

## Supported File Types

  Format                   Extension
  ------------------------ -----------
  Comma-separated values   `.csv`
  Excel workbook           `.xlsx`
  Legacy Excel workbook    `.xls`

The backend applies file validation and a configured upload-size limit.
Check the upload endpoint for the current limit and validation rules.

------------------------------------------------------------------------

## Privacy and Data Handling

InsightIQ processes uploaded files to provide analytics and generate
reports. The current implementation also saves dataset metadata and
analysis results in PostgreSQL and stores uploaded files for backend
processing and history functionality.

**Important:** Immediate deletion of original uploads and automatic
24-hour expiration of saved findings and reports have been discussed as
desired behavior, but should not be considered implemented until the
backend cleanup workflow has been added and tested.

Before using real or sensitive business data, review the current storage
behavior, restrict access to the backend, protect environment secrets,
and implement and verify an appropriate deletion policy.

------------------------------------------------------------------------

## Current Project Status

The core upload, analysis, dashboard, AI, forecasting, PDF-reporting,
PostgreSQL, and history features have been implemented and tested during
development.

This is a development project. Production deployment requires additional
configuration, security review, error monitoring, and testing with
representative datasets.

------------------------------------------------------------------------

## Future Improvements

Potential improvements include:

-   More robust handling of different dataset structures and business
    domains.
-   Improved saved-analysis viewing and filtering.
-   Configurable data-retention and automatic cleanup.
-   Stronger upload security, API rate limiting, and production
    deployment configuration.
-   More extensive automated tests.

------------------------------------------------------------------------

## Author

**Md. Nazibur Rahman**

GitHub: [nazibur74](https://github.com/nazibur74)

------------------------------------------------------------------------

## License

Choose and add a license before distributing or accepting contributions.
If no license is included, the repository's contents are not
automatically open for reuse.
