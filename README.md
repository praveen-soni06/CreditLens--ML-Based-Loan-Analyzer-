# 🏦 CreditLens – ML-Based Loan Analyzer

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-brightgreen?logo=flask)
![XGBoost](https://img.shields.io/badge/XGBoost-ML%20Model-orange)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightblue?logo=sqlite)
![License](https://img.shields.io/badge/License-Open%20Source-green)

**CreditLens** is an intelligent machine learning-powered loan analysis system that predicts loan approval outcomes using applicant financial and demographic data. It combines XGBoost classification models with an intuitive Flask-based web interface, multi-role user management, AI-powered explanations, and comprehensive application tracking for financial institutions.

---

## 📋 Overview

CreditLens addresses the critical need for fast, consistent, and explainable loan decisions. Financial institutions face challenges in automating initial screening while maintaining compliance and fairness. This system bridges that gap by:

- **Automating loan decisions** using machine learning models trained on historical data
- **Generating human-readable explanations** powered by Google Gemini or Hugging Face LLMs
- **Supporting multi-role workflows** with separate portals for loan assistants, credit managers, and applicants
- **Maintaining full audit trails** with email notifications and real-time status tracking

The system is production-ready with role-based access control, persistent data storage via SQLAlchemy ORM, and configurable AI providers for decision explanations.

### Key Features

✨ **Machine Learning Predictions** – XGBoost-based binary classification with SMOTE-balanced training  
🔐 **Multi-Role Authentication** – Session-based auth with credit manager and loan assistant roles  
📊 **Admin Dashboard** – Real-time metrics, application filtering, decision management, and analytics  
🤖 **AI Decision Explanations** – Google Gemini or Hugging Face integration with fallback to rule-based explanations  
📧 **Email Notifications** – Automated status updates to applicants with verification codes  
🔍 **Application Tracking Portal** – Applicants monitor loan status with event timeline  
📈 **Risk Scoring** – Multi-factor risk assessment with Low/Medium/High categorization  
💾 **SQLite Persistence** – Relational database with models for users, applications, predictions, verifications, and audit logs  
🎨 **Responsive UI** – Bootstrap-based Flask templates with form validation

---

## 🏗️ Architecture

CreditLens follows a modular, layered architecture:

```
┌─────────────────────────────────────┐
│   Flask Web Application             │
│  (Login, Forms, Dashboard, Tracking)│
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Business Logic Layer              │
│  (Prediction, Email, Explanations)  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   ML Pipeline                       │
│  (XGBoost Model + Scaler)           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   External Services                 │
│  (Gemini/HF APIs, SMTP Email)       │
└─────────────────────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   SQLAlchemy ORM Layer              │
│  (SQLite Database)                  │
└─────────────────────────────────────┘
```

### Data Flow

1. **Application Submission** → Loan Assistant submits form → Backend validation → Feature preprocessing
2. **ML Prediction** → XGBoost inference → Confidence & risk score calculation
3. **Explanation Generation** → AI provider (Gemini/HF) generates human-readable explanation
4. **Database Storage** → Application, prediction, explanation saved
5. **Admin Review** → Credit Manager reviews in dashboard → Approves/Rejects/Holds
6. **Notification** → Email sent to applicant with decision & explanation
7. **Tracking** → Applicant verifies email → Accesses tracking portal → Views status timeline

---

## ⚙️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Flask (Python web framework) |
| **ML Model** | XGBoost (binary classification) |
| **Data Processing** | Pandas, NumPy, Scikit-Learn, Imbalanced-Learn (SMOTE) |
| **Database** | SQLite 3 with SQLAlchemy ORM |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap |
| **Email Service** | SMTP (Gmail, custom providers) |
| **AI Providers** | Google Gemini API, Hugging Face Inference API |
| **Serialization** | Joblib (model/scaler persistence) |
| **Model Training** | Jupyter Notebook (notebooks/training.ipynb) |
| **Environment** | python-dotenv (configuration management) |

---

## 📁 Project Structure

```
CreditLens--ML-Based-Loan-Analyzer-/
├── app/                                 # Flask application package
│   ├── __init__.py                      # App factory, database init, blueprint registration
│   ├── database/
│   │   └── db.py                        # SQLAlchemy models (User, Application, Prediction, etc.)
│   ├── routes/
│   │   ├── auth.py                      # Login/logout endpoints
│   │   ├── main.py                      # Home page route
│   │   ├── predict.py                   # Loan application form & prediction submission
│   │   ├── dashboard.py                 # Admin dashboard & decision management
│   │   └── tracking.py                  # Applicant status tracking portal
│   ├── templates/
│   │   ├── base.html                    # Base template (header, nav, footer)
│   │   ├── index.html                   # Home page
│   │   ├── login.html                   # Authentication page
│   │   ├── dashboard.html               # Credit manager dashboard
│   │   ├── review.html                  # Application review interface
│   │   ├── result.html                  # Prediction results page
│   │   ├── submitted.html               # Application confirmation
│   │   ├── track.html                   # Tracking portal entry
│   │   ├── track_verify.html            # Email verification for tracking
│   │   ├── tracking_status.html         # Status display with timeline
│   │   ├── verify_email.html            # Email verification page
│   │   └── emails/                      # Email templates for notifications
│   ├── static/
│   │   ├── css/                         # Stylesheets (Bootstrap customizations)
│   │   ├── js/                          # Client-side JavaScript
│   │   └── images/                      # Images & assets
│   └── utils/
│       ├── email_utils.py               # SMTP email sending, verification code generation
│       ├── nlp_explainer.py             # AI explanation generation (Gemini/HF APIs)
│       └── lifecycle.py                 # Application status lifecycle management
│
├── ML/                                  # Machine Learning assets
│   ├── loan_data.csv                    # Training dataset (~3.6MB)
│   ├── model.pkl                        # Serialized XGBoost model
│   └── scaler.pkl                       # Serialized feature scaler (StandardScaler)
│
├── notebooks/
│   └── training.ipynb                   # Jupyter notebook for model training & evaluation
│
├── instance/                            # Runtime instance data (created at first run)
│   └── CreditLens.db                    # SQLite database (auto-generated)
│
├── .env.example                         # Environment variables template
├── .flaskenv                            # Flask environment configuration
├── .gitignore                           # Git ignore rules
├── requirements.txt                     # Python package dependencies
├── run.py                               # Application entry point
└── README.md                            # This file
```

### Key Directories Explained

| Directory | Purpose |
|-----------|---------|
| `app/` | Main Flask application package with all routes, templates, database models |
| `app/routes/` | Endpoint handlers for authentication, prediction, dashboard, tracking |
| `app/templates/` | Jinja2 HTML templates for UI rendering |
| `app/static/` | CSS, JavaScript, and image assets |
| `app/utils/` | Helper modules for email, NLP explanations, lifecycle management |
| `app/database/` | SQLAlchemy ORM model definitions (schema) |
| `ML/` | Pre-trained XGBoost model, feature scaler, training data |
| `notebooks/` | Jupyter notebook for model training, evaluation, hyperparameter tuning |
| `instance/` | Runtime files (SQLite database, generated at startup) |

---

## 🚀 Installation

### Prerequisites

- **Python 3.8+** (tested on Python 3.8, 3.9, 3.10, 3.11)
- **pip** (Python package manager)
- **Git** (for cloning)
- **Virtual Environment** (highly recommended)

### Step 1: Clone Repository

```bash
git clone https://github.com/praveen-soni06/CreditLens--ML-Based-Loan-Analyzer-.git
cd CreditLens--ML-Based-Loan-Analyzer-
```

### Step 2: Create & Activate Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Installed packages:
- Flask – Web framework
- python-dotenv – Environment configuration
- xgboost – ML model
- scikit-learn – ML utilities
- pandas – Data manipulation
- numpy – Numerical computing
- imbalanced-learn – SMOTE balancing
- flask-sqlalchemy – Database ORM
- joblib – Model serialization

### Step 4: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# SMTP Email Configuration (for Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_SENDER=your-email@gmail.com
EMAIL_SENDER_NAME=CreditLens Support

# Development: save emails locally if SMTP unavailable
EMAIL_DEV_OUTBOX=True
EMAIL_FALLBACK_TO_OUTBOX=True

# Support contact (displayed in emails/UI)
SUPPORT_EMAIL=support@creditlens.com
SUPPORT_PHONE=+91-00000-00000
SUPPORT_HOURS=Mon-Fri, 9:00 AM to 6:00 PM

# Application URLs
PORTAL_LOGIN_URL=http://127.0.0.1:5000/login
DEFAULT_LOAN_TENURE_MONTHS=36
MODEL_APPROVAL_CLASS_LABEL=0

# AI Provider Configuration (optional)
NLP_PROVIDER=auto  # Options: auto, gemini, huggingface, none
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL_NAME=gemini-1.5-flash
HUGGINGFACEHUB_API_TOKEN=your-hf-token
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
```

**Gmail Setup:**
1. Enable 2-Step Verification in Google Account settings
2. Generate app-specific password: https://myaccount.google.com/apppasswords
3. Use the generated password in `EMAIL_HOST_PASSWORD`

### Step 5: Initialize Database

The database is automatically created on first run. Manual initialization (optional):

```bash
python -c "from app import create_app; create_app()"
```

This creates `instance/CreditLens.db` and seeds demo users.

### Step 6: Run Application

```bash
python run.py
```

The application starts at **http://127.0.0.1:5000**

### Step 7: Verify Installation

1. Open browser to `http://localhost:5000`
2. Login with demo credentials:
   - **Email:** `admin@creditlens.com` | **Password:** `admin123` (Credit Manager)
   - **Email:** `assistant@creditlens.com` | **Password:** `assistant123` (Loan Assistant)

---

## 📖 Usage

### For Loan Assistants

**1. Login**
- Navigate to `http://localhost:5000/login`
- Enter: `assistant@creditlens.com` / `assistant123`

**2. Submit Application**
- Click "New Application" button
- Fill in applicant details:
  - Personal: Age, Gender, Education, Annual Income, Employment Experience
  - Home Ownership: OWN, RENT, MORTGAGE, or OTHER
  - Loan Details: Amount, Purpose (PERSONAL, EDUCATION, MEDICAL, VENTURE, HOMEIMPROVEMENT, DEBTCONSOLIDATION)
  - Credit Info: Credit Score, Credit History Length, Previous Loan Defaults
- Click "Submit Application"

**3. View Results**
- See ML prediction (Approved/Rejected)
- Review confidence score and risk category
- Read AI-generated explanation of decision

**4. Applicant Notification**
- Applicant receives verification email with tracking link
- Applicant can access tracking portal after email verification

### For Credit Managers

**1. Login**
- Navigate to `http://localhost:5000/login`
- Enter: `admin@creditlens.com` / `admin123`

**2. Access Dashboard**
- View key metrics: Total applications, Approval rate, Risk distribution
- Filter by status: Submitted, Underwriting, Approved, Rejected, Hold

**3. Review Applications**
- Click application to view full details
- Review ML decision, risk score, and AI explanation
- View applicant information and submission timeline

**4. Make Decision**
- Choose: Approve, Reject, or Hold
- Add optional remarks/comments for audit trail
- Decision recorded with timestamp and credit manager name

**5. Send Notifications**
- System automatically sends decision email to applicant
- Email includes decision, explanation, and next steps

### For Applicants (Tracking Portal)

**1. Access Tracking**
- Navigate to `http://localhost:5000/track`
- Enter Application Reference ID
- Verify email with code sent to applicant email

**2. View Status**
- See current application status
- Browse timeline of all status updates
- View final decision and explanation (if available)

---

## 🔌 API Endpoints

### Authentication Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/login` | User login |
| GET | `/logout` | User logout |

### Main Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |

### Prediction Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/application` | Loan application form page |
| POST | `/submit-application` | Submit application for ML prediction |
| GET | `/result/<ref_id>` | View prediction results for application |

### Dashboard Routes (Credit Manager Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard` | Dashboard home page |
| GET | `/dashboard/applications` | Get all applications (JSON) |
| GET | `/dashboard/application/<app_id>` | Get single application details (JSON) |
| POST | `/dashboard/review` | Submit credit manager decision |
| GET | `/dashboard/analytics` | Get dashboard analytics (JSON) |

### Tracking Routes (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/track` | Application tracking page |
| POST | `/verify-tracking` | Verify applicant email with code |
| GET | `/track-status/<ref_id>` | Get application status (JSON) |

### Example: Submit Application

**cURL Request:**
```bash
curl -X POST http://localhost:5000/submit-application \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "customer_name=John Doe" \
  -d "customer_email=john@example.com" \
  -d "person_age=35" \
  -d "person_gender=1" \
  -d "person_education=Graduate" \
  -d "person_income=60000" \
  -d "person_emp_exp=5" \
  -d "person_home_ownership=OWN" \
  -d "loan_amnt=20000" \
  -d "loan_intent=PERSONAL" \
  -d "loan_int_rate=8.5" \
  -d "loan_percent_income=0.33" \
  -d "credit_score=720" \
  -d "credit_history_length=10" \
  -d "previous_loan_defaults_on_file=0"
```

**Example Response:**
```json
{
  "status": "success",
  "reference_id": "APP20260720001",
  "prediction": "Approved",
  "confidence": 0.87,
  "risk_score": 0.25,
  "risk_category": "Low"
}
```

---

## 🗄️ Database Schema

CreditLens uses SQLite with SQLAlchemy ORM. Auto-created at first run (`instance/CreditLens.db`).

### Core Tables

#### `users`
Stores user accounts with role-based access:

| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary Key |
| name | String | User full name |
| email | String | Unique email |
| password | String | Password hash |
| role | String | `credit_manager` or `loan_assistant` |
| created_at | DateTime | Account creation |

#### `applications`
Loan applications submitted by assistants:

| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary Key |
| application_ref | String | Unique reference (e.g., APP20260720001) |
| loan_assistant_id | Integer | FK to users |
| customer_name | String | Applicant name |
| customer_email | String | Applicant email |
| person_age | Integer | Age in years |
| person_gender | SmallInt | 0=Female, 1=Male |
| person_education | String | Education level |
| person_income | Float | Annual income |
| person_emp_exp | Integer | Employment years |
| person_home_ownership | String | OWN, RENT, MORTGAGE, OTHER |
| loan_amnt | Float | Requested amount |
| loan_intent | String | Purpose (PERSONAL, EDUCATION, MEDICAL, etc.) |
| loan_int_rate | Float | Interest rate % |
| loan_percent_income | Float | Loan as % of income |
| credit_history_length | Float | Credit history years |
| credit_score | Integer | FICO score |
| previous_loan_defaults_on_file | SmallInt | 0=No, 1=Yes |
| submitted_at | DateTime | Submission timestamp |
| tracking_status | String | submitted, underwriting, approved, rejected, hold |
| review_queue | String | underwriting, review, hold |
| admin_remarks | Text | Credit manager comments |
| status_updated_at | DateTime | Last status update |

#### `predictions`
ML model predictions:

| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary Key |
| application_id | Integer | FK to applications |
| ml_decision | SmallInt | 0=Rejected, 1=Approved |
| confidence_score | Float | 0.0-1.0 model confidence |
| risk_score | Float | 0.0-1.0 risk level |
| risk_category | String | Low, Medium, High |
| flag | String | clear, review |
| final_decision | String | approved, rejected, pending, hold |
| decided_by | Integer | FK to users (Credit Manager) |
| decision_at | DateTime | Decision timestamp |
| email_sent | SmallInt | 0=No, 1=Yes |
| predicted_at | DateTime | Prediction timestamp |

#### `email_verifications`
Tracks email verification codes:

| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary Key |
| application_id | Integer | FK to applications |
| verification_code | String | OTP code |
| expires_at | DateTime | Code expiration |
| verified | Boolean | Verification status |
| attempts | Integer | Verification attempts |

#### `loan_decision_explanations`
AI-generated explanations:

| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary Key |
| application_id | Integer | FK to applications |
| prediction_id | Integer | FK to predictions |
| decision_result | String | approved, rejected, etc. |
| language_code | String | en, es, fr, etc. |
| provider | String | gemini, huggingface, rule_based |
| explanation_text | Text | Main explanation |
| financial_analysis | Text | Financial assessment |
| suggestions_text | Text | Improvement recommendations |
| risk_explanation | Text | Risk analysis |
| confidence_summary | Text | Confidence statement |
| smart_tips | Text | Tips for applicant |
| email_subject | String | Email subject |
| email_preview | Text | Email preview |
| created_at | DateTime | Creation timestamp |

#### `application_timeline_events`
Audit log of all events:

| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary Key |
| application_id | Integer | FK to applications |
| event_key | String | Unique event ID |
| title | String | Event title |
| description | Text | Event details |
| actor_role | String | system, manager, assistant |
| created_at | DateTime | Event timestamp |

### Relationships

```
User (1) ──→ (Many) Application
User (1) ──→ (Many) Prediction
Application (1) ──→ (1) Prediction
Application (1) ──→ (Many) EmailVerification
Application (1) ──→ (Many) LoanDecisionExplanation
Application (1) ──→ (Many) ApplicationTimelineEvent
```

---

## 🤖 Machine Learning

### Model Details

- **Type:** XGBoost (eXtreme Gradient Boosting)
- **Task:** Binary Classification (Approved/Rejected)
- **File:** `ML/model.pkl` (serialized with Joblib)
- **Training Data:** `ML/loan_data.csv` (~3.6MB, ~5000+ records)
- **Features:** 18 numerical and categorical applicant attributes
- **Balancing:** SMOTE (Synthetic Minority Over-Sampling) to handle class imbalance

### Preprocessing Pipeline

1. **Feature Loading** – Read loan_data.csv
2. **Categorical Encoding** – Convert gender, education, home ownership, loan intent to numerical
3. **Scaling** – StandardScaler normalization (saved in `ML/scaler.pkl`)
4. **SMOTE Balancing** – Address class imbalance in training set
5. **Train/Test Split** – 80/20 split for model evaluation

### Prediction Flow

1. **Input** → Applicant financial and demographic data
2. **Preprocessing** → Apply scaler (ML/scaler.pkl)
3. **Model Inference** → XGBoost binary classification
4. **Post-Processing:**
   - Extract prediction probability (confidence)
   - Calculate risk score (inverse confidence)
   - Categorize risk (Low: <0.33, Medium: 0.33-0.66, High: >0.66)
5. **Output** → `{prediction, confidence, risk_score, risk_category}`

### Model Retraining

To retrain with new data:

1. Update `ML/loan_data.csv` with new applicant records
2. Open `notebooks/training.ipynb` in Jupyter
3. Run all cells to train and save updated model/scaler
4. Restart Flask app to load new model

```bash
jupyter notebook notebooks/training.ipynb
```

### Evaluation Metrics

The training notebook computes:
- **Accuracy** – Overall correctness
- **Precision** – True approvals / All approvals (minimize false positives)
- **Recall** – True approvals / Actual approvals (catch defaults)
- **F1-Score** – Harmonic mean of precision & recall
- **ROC-AUC** – Model discrimination ability

---

## ⚙️ Configuration

### Flask Application Settings

File: `.flaskenv`

```shell
FLASK_APP=run.py
FLASK_ENV=development  # Use 'production' for deployment
```

### Email Configuration

File: `.env`

```env
# Gmail with app-specific password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Development mode (save emails locally)
EMAIL_DEV_OUTBOX=True
EMAIL_FALLBACK_TO_OUTBOX=True
```

### AI Provider Configuration

Choose one of these approaches:

**Option 1: Auto-detect (recommended)**
```env
NLP_PROVIDER=auto
GEMINI_API_KEY=your-key
HUGGINGFACEHUB_API_TOKEN=your-token
```

**Option 2: Google Gemini only**
```env
NLP_PROVIDER=gemini
GEMINI_API_KEY=your-key
GEMINI_MODEL_NAME=gemini-1.5-flash
```

**Option 3: Hugging Face only**
```env
NLP_PROVIDER=huggingface
HUGGINGFACEHUB_API_TOKEN=your-token
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2
```

**Option 4: Rule-based only (no external APIs)**
```env
NLP_PROVIDER=none
```

### Database Configuration

Default: SQLite (`sqlite:///CreditLens.db`)

For production with PostgreSQL, edit `app/__init__.py`:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@localhost:5432/creditlens"
```

### Application Settings

```env
DEFAULT_LOAN_TENURE_MONTHS=36        # Default loan term
MODEL_APPROVAL_CLASS_LABEL=0         # Approval class in model
PORTAL_LOGIN_URL=http://127.0.0.1:5000/login  # Login URL for emails
SECRET_KEY=Ex_Tracker                # Flask session key (change in production)
```

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution:** Ensure virtual environment is activated and requirements installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: Database file not found / Login with demo credentials fails

**Solution:** Reset database:
```bash
rm instance/CreditLens.db
python -c "from app import create_app; create_app()"
```

### Issue: SMTP ConnectionRefusedError when sending emails

**Solution:** Verify email configuration in `.env`:
- Enable 2-Step Verification in Google Account
- Generate app-specific password (not regular Gmail password)
- Use `EMAIL_PORT=465` with `EMAIL_USE_SSL=True`

For testing without SMTP:
```env
EMAIL_DEV_OUTBOX=True
EMAIL_FALLBACK_TO_OUTBOX=True
```

Emails are saved locally in `instance/mail_outbox/`.

### Issue: "API key not configured" for Gemini/Hugging Face

**Solution:** Add API keys to `.env`:
```env
GEMINI_API_KEY=your-key
HUGGINGFACEHUB_API_TOKEN=your-token
```

Or disable external APIs:
```env
NLP_PROVIDER=none
```

### Issue: Port 5000 already in use

**Solution:** Run on different port:
```bash
python -m flask run --port 5001
```

---

## 📊 Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask session encryption key | `Ex_Tracker` | No |
| `FLASK_ENV` | Environment mode | `development` | No |
| `EMAIL_HOST` | SMTP server | `smtp.gmail.com` | No |
| `EMAIL_PORT` | SMTP port | `465` | No |
| `EMAIL_USE_SSL` | Use SSL for SMTP | `True` | No |
| `EMAIL_HOST_USER` | Sender email account | `` | If sending emails |
| `EMAIL_HOST_PASSWORD` | Email password/token | `` | If sending emails |
| `EMAIL_SENDER` | Sender email display | Auto-detected | No |
| `EMAIL_SENDER_NAME` | Sender name display | `CreditLens Support` | No |
| `EMAIL_DEV_OUTBOX` | Save emails locally | `True` | No |
| `EMAIL_FALLBACK_TO_OUTBOX` | Fallback to local save | `True` | No |
| `SUPPORT_EMAIL` | Support contact email | Auto-detected | No |
| `SUPPORT_PHONE` | Support phone number | `+91-00000-00000` | No |
| `SUPPORT_HOURS` | Support hours display | `Mon-Fri, 9:00 AM to 6:00 PM` | No |
| `PORTAL_LOGIN_URL` | Portal URL in emails | `http://127.0.0.1:5000/login` | No |
| `DEFAULT_LOAN_TENURE_MONTHS` | Default loan term | `36` | No |
| `MODEL_APPROVAL_CLASS_LABEL` | Approval class label | `0` | No |
| `NLP_PROVIDER` | AI provider | `auto` | No |
| `GEMINI_API_KEY` | Google Gemini API key | `` | If using Gemini |
| `GEMINI_MODEL_NAME` | Gemini model version | `gemini-1.5-flash` | No |
| `HUGGINGFACEHUB_API_TOKEN` | Hugging Face API token | `` | If using HF |
| `HF_MODEL_NAME` | Hugging Face model | `mistralai/Mistral-7B-Instruct-v0.2` | No |

---

## 📦 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.8 | 3.10+ |
| **RAM** | 2GB | 4GB+ |
| **Disk Space** | 500MB | 1GB+ |
| **OS** | Linux, macOS, Windows | Any |

**Optional:**
- CUDA/GPU for faster model training
- PostgreSQL for production database

---

## 🔄 Application Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. LOAN ASSISTANT SUBMITS APPLICATION                      │
│    - Fills applicant details via web form                  │
│    - Backend validates and saves to database               │
│    - Generates unique reference ID                         │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 2. ML PREDICTION                                            │
│    - Preprocesses features (scaling, encoding)             │
│    - XGBoost model inference                               │
│    - Calculates confidence & risk scores                   │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 3. EXPLANATION GENERATION                                   │
│    - Calls Gemini or Hugging Face API                      │
│    - Generates human-readable explanation                  │
│    - Falls back to rule-based if API fails                 │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 4. DATABASE STORAGE                                         │
│    - Saves application, prediction, explanation            │
│    - Creates timeline event                                │
│    - Sends email notification to applicant                 │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 5. ADMIN REVIEW (CREDIT MANAGER DASHBOARD)                 │
│    - Reviews ML decision & AI explanation                  │
│    - Approves, Rejects, or Holds application              │
│    - Adds optional remarks                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 6. FINAL NOTIFICATION                                       │
│    - Sends final decision email to applicant               │
│    - Includes decision, explanation, next steps            │
│    - Provides tracking portal access                       │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 7. APPLICANT TRACKING                                       │
│    - Applicant verifies email                              │
│    - Accesses tracking portal                              │
│    - Views application status & timeline                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Development & Deployment

### Development Mode

```bash
python run.py
```

Features:
- Hot reload on code changes
- Detailed error messages
- SMTP fallback to local email save

### Production Deployment

#### Using Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

#### Using Docker (optional):

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

#### Production .env settings:

```env
FLASK_ENV=production
SECRET_KEY=generate-a-random-key
EMAIL_HOST_USER=your-production-email
EMAIL_HOST_PASSWORD=your-app-password
GEMINI_API_KEY=your-production-key
```

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [Scikit-Learn Documentation](https://scikit-learn.org/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Hugging Face API](https://huggingface.co/docs/api-inference)

---

## 📄 License

This project is open-source. No LICENSE file currently exists in the repository. Please add a license (e.g., MIT, Apache 2.0) based on your intended distribution terms.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/YourFeature`
3. **Commit** your changes: `git commit -m 'Add YourFeature'`
4. **Push** to the branch: `git push origin feature/YourFeature`
5. **Open** a Pull Request with detailed description

### Development Guidelines

- Use virtual environments for isolation
- Test all changes before submitting PR
- Update README if adding new features
- Follow PEP 8 Python style guide
- Add docstrings to new functions/classes

---

## 📞 Support & Issues

**For issues, questions, or feature requests:**

1. Check the [Troubleshooting](#-troubleshooting) section above
2. Search existing [GitHub Issues](https://github.com/praveen-soni06/CreditLens--ML-Based-Loan-Analyzer-/issues)
3. Create a new issue with:
   - Clear title and description
   - Steps to reproduce (if applicable)
   - Python/Flask/XGBoost versions
   - Error logs or stack trace

---

## ⭐ Acknowledgments

- **XGBoost** – Powerful gradient boosting framework
- **Flask** – Lightweight and flexible web framework
- **Scikit-Learn** – ML utilities and preprocessing
- **SQLAlchemy** – Elegant ORM for database operations
- **Google Gemini & Hugging Face** – AI-powered explanations
- **Bootstrap** – Responsive UI framework
- The open-source community for amazing tools and libraries

---

## 👨‍💻 Author

**Praveen Soni**  
GitHub: [@praveen-soni06](https://github.com/praveen-soni06)  
Repository: [CreditLens--ML-Based-Loan-Analyzer-](https://github.com/praveen-soni06/CreditLens--ML-Based-Loan-Analyzer-)

---

**Last Updated:** July 2026  
**Version:** 1.0.0  
**Status:** Active Development
