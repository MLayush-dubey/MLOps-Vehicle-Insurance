# 🚗 Vehicle Insurance MLOps

An end-to-end MLOps project for predicting vehicle insurance cross-sell outcomes — from raw data ingestion to a Dockerized API deployed on AWS EC2 with a full CI/CD pipeline.

---

## 📌 Overview

This project implements a production-grade machine learning pipeline to predict whether a customer is likely to opt for vehicle insurance. It demonstrates best practices in MLOps: modular code structure, automated training pipelines, cloud model storage, and continuous deployment via GitHub Actions.

---

## 🏗️ Architecture

```
MongoDB Atlas (Raw Data)
        ↓
Data Ingestion → Data Validation → Data Transformation
        ↓
   Model Trainer → Model Evaluation → Model Pusher (AWS S3)
        ↓
   FastAPI Prediction App (Dockerized)
        ↓
   AWS EC2 via GitHub Actions CI/CD
```

---

## ⚙️ Tech Stack

| Category | Tools |
|---|---|
| **Language** | Python 3.10 |
| **ML & Data** | Scikit-learn, Pandas, NumPy |
| **Database** | MongoDB Atlas |
| **Cloud Storage** | AWS S3 |
| **Deployment** | AWS EC2, Docker, ECR |
| **CI/CD** | GitHub Actions (Self-hosted Runner) |
| **API** | Flask / FastAPI |
| **Environment** | Conda |

---

## 📁 Project Structure

```
vehicle-insurance-mlops/
├── src/
│   ├── components/          # Pipeline components (ingestion, validation, etc.)
│   ├── configuration/       # MongoDB & AWS connection configs
│   ├── cloud_storage/       # AWS S3 storage utilities
│   ├── data_access/         # Data fetch & transform layer
│   ├── entity/              # Config & artifact entities, estimator
│   ├── pipeline/            # Training pipeline orchestration
│   └── utils/               # Shared utilities
├── config/
│   └── schema.yaml          # Dataset schema for validation
├── notebook/                # EDA & feature engineering notebooks
├── static/ & templates/     # Frontend for prediction UI
├── app.py                   # Application entry point
├── demo.py                  # Pipeline test runner
├── Dockerfile
├── requirements.txt
├── setup.py
└── pyproject.toml
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/vehicle-insurance-mlops.git
cd vehicle-insurance-mlops
```

### 2. Set up the environment

```bash
conda create -n vehicle python=3.10 -y
conda activate vehicle
pip install -r requirements.txt
```

### 3. Configure environment variables

**Bash:**
```bash
export MONGODB_URL="mongodb+srv://<username>:<password>@cluster.mongodb.net/"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

**PowerShell:**
```powershell
$env:MONGODB_URL = "mongodb+srv://<username>:<password>@cluster.mongodb.net/"
$env:AWS_ACCESS_KEY_ID = "your-access-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-key"
```

### 4. Run the training pipeline

```bash
python demo.py
```

### 5. Start the application

```bash
python app.py
```

---

## ☁️ Cloud Setup

### MongoDB Atlas
- Create a free M0 cluster
- Add `0.0.0.0/0` to Network Access for broad connectivity
- Push data to the cluster using `notebook/mongoDB_demo.ipynb`

### AWS
- **IAM**: Create a user with `AdministratorAccess` and generate access keys
- **S3**: Create a bucket named `my-model-mlopsproj` (region: `us-east-1`) for model registry
- **ECR**: Create a repository named `vehicleproj` to store Docker images
- **EC2**: Launch an Ubuntu 24.04 `t2.medium` instance with 30GB storage; expose port `5080`

---

## 🔄 CI/CD Pipeline

The pipeline is triggered on every push to the main branch via GitHub Actions.

**Workflow:**
1. Build Docker image
2. Push to AWS ECR
3. Pull and run on self-hosted EC2 runner

**Required GitHub Secrets:**

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key |
| `AWS_DEFAULT_REGION` | `us-east-1` |
| `ECR_REPO` | ECR repository URI |

---

## 🌐 Endpoints

| Route | Description |
|---|---|
| `/` | Prediction UI |
| `/training` | Trigger model training |

App is accessible at: `http://<EC2-PUBLIC-IP>:5080`

---

## 📊 Pipeline Components

| Component | Responsibility |
|---|---|
| **Data Ingestion** | Fetches data from MongoDB, splits into train/test sets |
| **Data Validation** | Schema checks against `schema.yaml` |
| **Data Transformation** | Feature engineering, preprocessing |
| **Model Trainer** | Trains and evaluates candidate model |
| **Model Evaluation** | Compares against production model (threshold: `0.02`) |
| **Model Pusher** | Pushes best model to AWS S3 registry |

---

## 📝 License

This project is for educational and portfolio purposes.
