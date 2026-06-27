# Automated Data Ingestion & Cloud Sync Pipeline 🚀

A cloud-ready ETL pipeline that automates the extraction, normalization, and synchronization of daily agricultural market data. Built with Python, Selenium, Pandas, and GitHub Actions for reliable, secure, and scalable data ingestion.

---

## 🏗️ Architecture

```text
Dynamic Web Source
        │
        ▼
Headless Chrome (Selenium)
        │
        ▼
Pandas Data Transformation
        │
        ▼
Cloud Storage Synchronization
        ▲
GitHub Actions + Secure Environment Secrets
```

---

## ✨ Features

- Headless browser automation using Selenium.
- Automated ETL workflow powered by GitHub Actions.
- Dynamic web scraping with asynchronous page handling.
- Data cleaning and normalization using Pandas.
- Secure cloud synchronization with encrypted environment variables.
- Self-healing exception handling for uninterrupted execution.
- Dashboard-ready output for analytics and Power BI.

---

## 📂 Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── scrape.yml
├── scraper.py
├── requirements.txt
├── README.md
└── Master_Schema.csv
```

---

## 🛠️ Tech Stack

- Python 3.10+
- Selenium
- Pandas
- NumPy
- Google Drive API
- GitHub Actions

---

## 🔐 Environment Variables

Configure the following secrets before running the pipeline:

| Secret | Purpose |
|---------|---------|
| `SOURCE_PIPELINE_URL` | Source website URL |
| `DRIVE_FILE_ID` | Target cloud file ID |
| `GCP_CREDENTIALS` | Google Cloud Service Account JSON |

---

## 📊 Output Schema

| Column | Description |
|---------|-------------|
| state | State name |
| district | District |
| market | Market/Mandi |
| commodity | Commodity |
| variety | Variety |
| min_price | Minimum price |
| max_price | Maximum price |
| modal_price | Modal price |
| arrival_date | Data collection date |

---

## ⚙️ Workflow

1. Launch headless browser.
2. Extract mandi data.
3. Normalize and clean records.
4. Validate schema.
5. Upload to cloud storage.
6. Trigger downstream analytics.

---

## 📌 Highlights

- Cloud-ready and fully automated
- Secure secret management
- Standardized relational dataset
- Dashboard and API integration ready
- Easily deployable on GitHub Actions

---

## 📄 License

This repository is intended as a portfolio demonstration of an automated cloud ETL pipeline. Sensitive infrastructure details and production endpoints have been abstracted for security.
