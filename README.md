# 🏦 CreditLens – ML-Based Loan Analyzer

**An intelligent machine learning-powered loan analysis system that predicts loan approval outcomes using applicant financial and demographic data, with an intuitive Flask-based web interface.**

---

## 📋 Overview

CreditLens is a comprehensive loan decision support system designed for financial institutions and loan service providers. It combines machine learning-powered loan predictions with a user-friendly web interface, comprehensive applicant tracking, and advanced decision explanations powered by AI models or rule-based analysis.

### What It Does
- **Automated Loan Predictions**: Predicts loan approval outcomes using XGBoost classification models trained on historical loan data
- **Risk Assessment**: Calculates and categorizes loan applicant risk levels based on financial and demographic factors
- **AI-Powered Explanations**: Generates human-readable explanations for loan decisions using Google Gemini or Hugging Face LLMs (with fallback to rule-based explanations)
- **Application Tracking**: Applicants can track their loan application status in real-time
- **Admin Dashboard**: Credit managers can review, approve, reject, or hold applications with detailed analytics
- **Email Notifications**: Sends automated status updates and decision notifications to applicants
- **Multi-Role Support**: Supports two user roles: Loan Assistants (submit applications) and Credit Managers (review decisions)

### Why It Was Built
Financial institutions need to make fast, consistent, and fair loan decisions while maintaining compliance and explainability. CreditLens bridges this gap by automating initial screening with machine learning while preserving human oversight through an intuitive dashboard.

### Key Features
✨ **Machine Learning Predictions** – XGBoost-based model with SMOTE-balanced training data  
🔐 **User Authentication** – Multi-role access control (Loan Assistants & Credit Managers)  
📊 **Advanced Analytics** – Comprehensive dashboard with real-time metrics and decision tracking  
🤖 **AI Decision Explanations** – Google Gemini or Hugging Face integration for natural language explanations  
📧 **Email Notifications** – Automated applicant communications with verification codes  
🔍 **Application Tracking** – Applicants can monitor their loan status with timeline events  
📈 **Risk Scoring** – Multi-factor risk assessment with categorization  
⚡ **SQLite Database** – Persistent storage with relational models for users, applications, predictions, and audit logs  
🎨 **Responsive UI** – Modern Flask templates with Bootstrap styling

---

## 🎬 Demo

### Live Demo
[Coming Soon]

### Screenshots

#### Home Page / Application Form
![Application Form](docs/images/application-form.png)

#### Prediction Results
![Prediction Results](docs/images/prediction-results.png)

#### Admin Dashboard
![Admin Dashboard](docs/images/admin-dashboard.png)

#### Tracking Status
![Application Tracking](docs/images/tracking-status.png)

*Screenshots placeholder – Add actual screenshots to `docs/images/` directory*

### Video Demo
[Coming Soon]

---

## ⚙️ Tech Stack

### **Frontend**
- Flask (Web Framework)
- HTML5
- CSS3
- JavaScript (Vanilla & Bootstrap)

### **Backend**
- Flask (Python Web Framework)
- Flask-SQLAlchemy (ORM)
- SQLite (Database)

### **Machine Learning / AI**
- XGBoost (Classification Model)
- Scikit-Learn (Model evaluation & preprocessing)
- Imbalanced-Learn (SMOTE for data balancing)
- Pandas & NumPy (Data manipulation)
- Google Gemini API (NLP Explanations)
- Hugging Face API (Alternative NLP Provider)

### **Database**
- SQLite 3 (Lightweight relational database)
- SQLAlchemy ORM (Database abstraction)

### **APIs & Integrations**
- Google Gemini API (AI Explanations)
- Hugging Face Inference API (Alternative AI Explanations)
- SMTP (Email notifications)

### **Authentication**
- Session-based authentication
- Role-based access control (RBAC)

### **Deployment**
- Python WSGI application
- Flask development server (development)
- Gunicorn/uWSGI ready (production)

### **Programming Languages**
- Python 3.8+
- HTML/CSS/JavaScript

### **Libraries & Tools**
- **Flask**: Web framework
- **python-dotenv**: Environment variable management
- **xgboost**: Machine learning model
- **scikit-learn**: ML utilities
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **imbalanced-learn**: Class balancing
- **flask-sqlalchemy**: Database ORM
- **joblib**: Model serialization

### **Development Tools**
- Git (Version control)
- Jupyter Notebook (ML model training & analysis)
- PyCharm IDE compatible

---

## 📁 Project Structure

```
CreditLens--ML-Based-Loan-Analyzer-/
├── app/                                 # Flask application package
│   ├── __init__.py                      # App factory & initialization
│   ├── database/
│   │   └── db.py                        # Database models (User, Application, Prediction, etc.)
│   ├── routes/
│   │   ├── auth.py                      # Authentication (login/logout)
│   │   ├── main.py                      # Home page routes
│   │   ├── predict.py                   # Loan application form & prediction
│   │   ├── dashboard.py                 # Admin dashboard & decision management
│   │   └── tracking.py                  # Application status tracking
│   ├── templates/
│   │   ├── base.html                    # Base template
│   │   ├── index.html                   # Home page
│   │   ├── login.html                   # Login page
│   │   ├── dashboard.html               # Admin dashboard
│   │   ├── review.html                  # Application review interface
│   │   ├── result.html                  # Prediction results
│   │   ├── submitted.html               # Application submitted confirmation
│   │   ├── track.html                   # Application tracking page
│   │   ├── track_verify.html            # Email verification for tracking
│   │   ├── tracking_status.html         # Tracking status display
│   │   ├── verify_email.html            # Email verification page
│   │   └── emails/                      # Email templates
│   ├── static/
│   │   ├── css/                         # Stylesheets
│   │   ├── js/                          # JavaScript files
│   │   └── images/                      # Images & assets
│   └── utils/
│       ├── email_utils.py               # Email sending & verification
│       ├── nlp_explainer.py             # AI explanation generation (Gemini/HF)
│       └── lifecycle.py                 # Application lifecycle management
│
├── ML/                                  # Machine Learning models & data
│   ├── loan_data.csv                    # Training dataset
│   ├── model.pkl                        # Trained XGBoost model
│   └── scaler.pkl                       # Feature scaler
│
├── notebooks/
│   └── training.ipynb                   # Model training & evaluation notebook
│
├── Dataset/                             # Additional datasets (if any)
│
├── instance/                            # Instance folder (database, cache)
│   └── CreditLens.db                    # SQLite database (generated)
│
├── .env.example                         # Environment variables template
├── .flaskenv                            # Flask environment config
├── .gitignore                           # Git ignore rules
├── requirements.txt                     # Python dependencies
├── run.py                               # Application entry point
└── README.md                            # This file

```

### Key Directories Explained

| Directory | Purpose |
|-----------|---------|
| `app/` | Main Flask application with routes, templates, database models, and utilities |
| `app/routes/` | API route handlers for authentication, prediction, dashboard, and tracking |
| `app/templates/` | Jinja2 HTML templates for UI rendering |
| `app/static/` | CSS, JavaScript, and image assets |
| `app/utils/` | Utility modules for email, NLP explanations, and lifecycle management |
| `app/database/` | SQLAlchemy ORM models defining database schema |
| `ML/` | Pre-trained machine learning models and training data |
| `notebooks/` | Jupyter notebooks for model training and analysis |

---

## 🚀 Installation

Follow these steps to set up CreditLens on your local machine:

### Prerequisites
- **Python 3.8 or higher**
- **pip** (Python package manager)
- **Git**
- **Virtual Environment** (recommended)

### Step 1: Clone the Repository
```bash
git clone https://github.com/praveen-soni06/CreditLens--ML-Based-Loan-Analyzer-.git
cd CreditLens--ML-Based-Loan-Analyzer-
```

### Step 2: Create and Activate Virtual Environment
```bash
# On Linux/macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the example environment file and update with your settings:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_SENDER=your-email@gmail.com
EMAIL_SENDER_NAME=CreditLens Support

# AI Configuration (Optional)
GEMINI_API_KEY=your-gemini-api-key
HUGGINGFACEHUB_API_TOKEN=your-hf-token
NLP_PROVIDER=auto  # Options: auto, gemini, huggingface, none

# Application Settings
DEFAULT_LOAN_TENURE_MONTHS=36
MODEL_APPROVAL_CLASS_LABEL=0
PORTAL_LOGIN_URL=http://127.0.0.1:5000/login
```

### Step 5: Initialize Database
The database is automatically created when you first run the application, but you can manually initialize it:
```bash
python -c "from app import create_app; create_app()"
```

### Step 6: Start the Flask Application
```bash
# Development mode with auto-reload
python run.py

# Or using Flask CLI
flask run
```

The application will be available at: **http://127.0.0.1:5000**

### Step 7: Verify Installation
1. Open your browser and navigate to `http://localhost:5000`
2. Login with demo credentials:
   - **Email**: `admin@creditlens.com` | **Password**: `admin123` (Credit Manager)
   - **Email**: `assistant@creditlens.com` | **Password**: `assistant123` (Loan Assistant)

---

## 🔐 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key for session encryption | No | `Ex_Tracker` |
| `EMAIL_HOST` | SMTP server hostname | No | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP server port | No | `465` |
| `EMAIL_USE_SSL` | Use SSL for email | No | `True` |
| `EMAIL_HOST_USER` | Email account for sending | Yes (if emails enabled) | - |
| `EMAIL_HOST_PASSWORD` | Email account password or app password | Yes (if emails enabled) | - |
| `EMAIL_SENDER` | Sender email address | No | Auto-detected from HOST_USER |
| `EMAIL_SENDER_NAME` | Sender display name | No | `CreditLens Support` |
| `EMAIL_DEV_OUTBOX` | Save emails locally in development | No | `True` |
| `EMAIL_FALLBACK_TO_OUTBOX` | Fallback to local save if SMTP fails | No | `True` |
| `SUPPORT_EMAIL` | Support contact email | No | Auto-detected |
| `SUPPORT_PHONE` | Support phone number | No | `+91-00000-00000` |
| `SUPPORT_HOURS` | Support hours display | No | `Mon-Fri, 9:00 AM to 6:00 PM` |
| `PORTAL_LOGIN_URL` | Portal login URL for emails | No | `http://127.0.0.1:5000/login` |
| `DEFAULT_LOAN_TENURE_MONTHS` | Default loan term in months | No | `36` |
| `MODEL_APPROVAL_CLASS_LABEL` | Class label for approval in model | No | `0` |
| `NLP_PROVIDER` | AI provider for explanations | No | `auto` |
| `GEMINI_API_KEY` | Google Gemini API key | No (if using Gemini) | - |
| `GEMINI_MODEL_NAME` | Gemini model version | No | `gemini-1.5-flash` |
| `HUGGINGFACEHUB_API_TOKEN` | Hugging Face API token | No (if using HF) | - |
| `HF_MODEL_NAME` | Hugging Face model name | No | `mistralai/Mistral-7B-Instruct-v0.2` |

---

## 📋 Requirements

### System Requirements
- **Python Version**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **RAM**: 2GB minimum (4GB recommended for model training)
- **Disk Space**: 500MB (including model files and database)

### Optional Requirements
- **CUDA/GPU**: Not required but speeds up model training
- **Google Gemini API**: For AI-powered decision explanations (free tier available)
- **Hugging Face API**: Alternative AI provider for explanations

### Python Package Requirements
See `requirements.txt`:
- Flask
- python-dotenv
- xgboost
- scikit-learn
- pandas
- numpy
- imbalanced-learn
- flask-sqlalchemy
- joblib

---

## 📖 Usage

### For Loan Assistants

#### 1. **Login**
- Navigate to `http://localhost:5000/login`
- Enter credentials: `assistant@creditlens.com` / `assistant123`

#### 2. **Submit a Loan Application**
- Click on "New Application"
- Fill in applicant details:
  - Personal Information (Age, Gender, Education, Income, Employment Experience)
  - Home Ownership status
  - Loan Details (Amount, Intent, Interest Rate)
  - Credit Information (Credit Score, History Length, Previous Defaults)
- Click "Submit Application"

#### 3. **View Results**
- After submission, the ML model predicts the outcome
- Review decision, risk score, and confidence level
- AI-generated explanation appears on results page

#### 4. **Applicant Verification**
- Applicant receives verification email with tracking link
- Applicant verifies email to unlock tracking

### For Credit Managers

#### 1. **Login**
- Navigate to `http://localhost:5000/login`
- Enter credentials: `admin@creditlens.com` / `admin123`

#### 2. **Access Dashboard**
- View all submitted applications
- See analytics: total applications, approval rate, risk distribution
- Filter applications by status (Submitted, Underwriting, Approved, Rejected)

#### 3. **Review Applications**
- Click on an application to view details
- Review ML decision, risk assessment, and explanation
- View applicant information and timeline

#### 4. **Make Decisions**
- Approve, Reject, or Hold application
- Add remarks/comments for audit trail
- Decision is recorded with timestamp

#### 5. **Send Notifications**
- System automatically sends decision emails to applicants
- Emails include personalized explanations

### For Applicants (Tracking)

#### 1. **Access Tracking Portal**
- Navigate to `http://localhost:5000/track`
- Enter Application Reference ID
- Verify email with code sent to applicant email

#### 2. **View Application Status**
- See current status (Submitted, Under Review, Approved, Rejected)
- View timeline of all events/updates
- See decision details if available

---

## 🔌 API Documentation

CreditLens provides backend routes for loan prediction and application management:

### Authentication Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/login` | User login page & form handler |
| GET | `/logout` | User logout |

### Main Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |

### Prediction Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/application` | Loan application form |
| POST | `/submit-application` | Submit application for prediction |
| GET | `/result/<ref_id>` | View prediction results |

### Dashboard Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard` | Admin dashboard (Credit Manager only) |
| GET | `/dashboard/applications` | List all applications (JSON) |
| GET | `/dashboard/application/<app_id>` | Get application details (JSON) |
| POST | `/dashboard/review` | Submit decision on application |
| GET | `/dashboard/analytics` | Get dashboard analytics (JSON) |

### Tracking Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/track` | Application tracking page |
| POST | `/verify-tracking` | Verify applicant email |
| GET | `/track-status/<ref_id>` | Get application status |

### Example: Submit Application

**Request:**
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
  -d "credit_history_length=10" \
  -d "credit_score=720" \
  -d "previous_loan_defaults_on_file=0"
```

**Response:**
```json
{
  "reference_id": "APP123456",
  "status": "success",
  "prediction": "approved",
  "confidence": 0.87,
  "risk_score": 0.25,
  "risk_category": "Low"
}
```

---

## 🗄️ Database

### Overview
CreditLens uses **SQLite** for data persistence with **SQLAlchemy ORM** for database operations.

Database file: `instance/CreditLens.db` (auto-created on first run)

### Database Schema

#### **users** table
Stores user accounts with role-based access:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| name | String | User name |
| email | String | Email (unique) |
| password | String | Password hash |
| role | Enum | `credit_manager` or `loan_assistant` |
| created_at | DateTime | Account creation timestamp |

#### **applications** table
Stores loan applications submitted by assistants:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| application_ref | String | Unique reference ID (e.g., APP123456) |
| loan_assistant_id | Integer | Foreign Key to users |
| customer_name | String | Applicant name |
| customer_email | String | Applicant email |
| person_age | Integer | Age |
| person_gender | SmallInt | 0 or 1 (Male/Female) |
| person_education | String | Education level |
| person_income | Float | Annual income |
| person_emp_exp | Integer | Employment experience (years) |
| person_home_ownership | String | HOME, RENT, OWN, MORTGAGE |
| loan_amnt | Float | Loan amount requested |
| loan_intent | String | Purpose (PERSONAL, EDUCATION, MEDICAL, etc.) |
| loan_int_rate | Float | Interest rate |
| loan_percent_income | Float | Loan as % of income |
| credit_history_length | Float | Credit history duration |
| credit_score | Integer | Credit score |
| previous_loan_defaults_on_file | SmallInt | 0 or 1 |
| submitted_at | DateTime | Submission timestamp |
| tracking_status | String | submitted, underwriting, approved, rejected, etc. |
| review_queue | String | underwriting, review, hold, etc. |
| admin_remarks | Text | Reviewer comments |
| status_updated_at | DateTime | Last status update |

#### **predictions** table
Stores ML model predictions:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| application_id | Integer | Foreign Key to applications |
| ml_decision | SmallInt | 0=Rejected, 1=Approved |
| confidence_score | Float | Model confidence (0-1) |
| risk_score | Float | Risk score |
| risk_category | String | Low, Medium, High |
| flag | Enum | clear or review |
| final_decision | Enum | approved, rejected, pending, hold |
| decided_by | Integer | Foreign Key to users (Credit Manager) |
| decision_at | DateTime | Decision timestamp |
| email_sent | SmallInt | 0 or 1 |
| predicted_at | DateTime | Prediction timestamp |

#### **email_verifications** table
Tracks email verification for tracking portal:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| application_id | Integer | Foreign Key to applications |
| verification_code | String | OTP/Code |
| expires_at | DateTime | Code expiration time |
| verified | Boolean | Verification status |
| attempts | Integer | Verification attempts |

#### **loan_decision_explanations** table
Stores AI-generated decision explanations:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| application_id | Integer | Foreign Key |
| prediction_id | Integer | Foreign Key |
| decision_result | String | approved, rejected, etc. |
| language_code | String | en, es, etc. |
| provider | String | gemini, huggingface, rule_based |
| explanation_text | Text | Main explanation |
| financial_analysis | Text | Financial assessment |
| suggestions_text | Text | Improvement suggestions |
| risk_explanation | Text | Risk analysis |
| confidence_summary | Text | Confidence statement |
| smart_tips | Text | Tips for applicant |
| email_subject | String | Email subject |
| email_preview | Text | Email preview |
| created_at | DateTime | Creation timestamp |

#### **application_timeline_events** table
Audit log of all application events:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| application_id | Integer | Foreign Key |
| event_key | String | Unique event identifier |
| title | String | Event title |
| description | Text | Event details |
| actor_role | String | Who triggered event (system, manager, assistant) |
| created_at | DateTime | Event timestamp |

### Entity Relationships

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

### Dataset
- **File**: `ML/loan_data.csv`
- **Size**: ~3.6MB with multiple applicant records
- **Features**: 18 input features (age, income, credit score, loan details, etc.)
- **Target**: Binary classification (Approved/Rejected)

### Model
- **Type**: XGBoost (eXtreme Gradient Boosting)
- **File**: `ML/model.pkl`
- **Training**: SMOTE-balanced dataset to handle class imbalance
- **Serialization**: Joblib pickle format

### Preprocessing
- **Scaler**: `ML/scaler.pkl` (StandardScaler from scikit-learn)
- **Feature Engineering**: Numerical encoding of categorical features
- **SMOTE**: Synthetic Minority Over-Sampling Technique for balanced training

### Training Process
The model is trained in the Jupyter notebook (`notebooks/training.ipynb`):
1. Load loan data
2. Handle missing values
3. Encode categorical variables (gender, education, home ownership, loan intent)
4. Apply SMOTE for class balancing
5. Split into train/test sets
6. Train XGBoost classifier
7. Evaluate with accuracy, precision, recall, F1-score
8. Save model and scaler

### Prediction Flow
1. **Input**: Applicant financial and demographic data
2. **Preprocessing**: Scale features using scaler.pkl
3. **Model Inference**: XGBoost predicts approval probability
4. **Post-Processing**: 
   - Extract confidence score (max probability)
   - Calculate risk score (1 - confidence for approved, confidence for rejected)
   - Categorize risk (Low < 0.33, Medium 0.33-0.66, High > 0.66)
5. **Output**: Prediction (Approved/Rejected), Confidence, Risk Score

### Evaluation Metrics
- **Accuracy**: Overall correctness
- **Precision**: True positives / All positives (minimize false approvals)
- **Recall**: True positives / Actual positives (catch defaults)
- **F1-Score**: Harmonic mean of precision & recall
- **ROC-AUC**: Model discrimination ability

### Model Retraining
To retrain the model with new data:
1. Update `ML/loan_data.csv` with new applicant records
2. Open `notebooks/training.ipynb` in Jupyter
3. Run all cells to train and save updated model
4. Restart Flask application to load new model

---

## 🔧 Configuration

### Application Settings

Edit `.flaskenv` for Flask configuration:
```shell
FLASK_APP=run.py
FLASK_ENV=development  # Change to 'production' for deployment
```

### Email Configuration

In `.env`:
```env
# Gmail Example
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Use app-specific password, not regular password

# Development (saves emails locally if SMTP fails)
EMAIL_DEV_OUTBOX=True
EMAIL_FALLBACK_TO_OUTBOX=True
```

**Generate Gmail App Password**:
1. Enable 2-Step Verification in Google Account
2. Go to App Passwords section
3. Generate app-specific password
4. Use in `EMAIL_HOST_PASSWORD`

### AI Provider Configuration

```env
# Option 1: Auto-detect (tries Gemini, falls back to Hugging Face)
NLP_PROVIDER=auto

# Option 2: Only use Gemini
NLP_PROVIDER=gemini
GEMINI_API_KEY=your-api-key
GEMINI_MODEL_NAME=gemini-1.5-flash

# Option 3: Only use Hugging Face
NLP_PROVIDER=huggingface
HUGGINGFACEHUB_API_TOKEN=your-token
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.2

# Option 4: Rule-based only (no external APIs)
NLP_PROVIDER=none
```

### Database Configuration

In `app/__init__.py`:
```python
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///CreditLens.db"  # SQLite
# Or use PostgreSQL for production:
# "postgresql://user:password@localhost/creditlens"
```

---

## 📸 Screenshots

### Home Page
![Home Page](docs/images/home.png)
*Application submission interface*

### Prediction Results
![Prediction Results](docs/images/prediction-results.png)
*ML decision with AI explanation*

### Admin Dashboard
![Admin Dashboard](docs/images/admin-dashboard.png)
*Credit manager review interface*

### Tracking Portal
![Tracking Portal](docs/images/tracking.png)
*Applicant status tracking*

---

## 🔄 Workflow

CreditLens follows this loan decision workflow:

```mermaid
flowchart LR
    A["Applicant"] -->|Fills Form| B["Loan Assistant Portal"]
    B -->|Submits Application| C["Flask Backend"]
    C -->|Feature Engineering| D["ML Model XGBoost"]
    D -->|Prediction| E["Risk Scoring"]
    E -->|Calculate Metrics| F["Generate Explanation"]
    F -->|Gemini/HF/Rule-Based| G["Store in Database"]
    G -->|Email Notification| H["Applicant"]
    G -->|Queue for Review| I["Credit Manager Dashboard"]
    I -->|Review & Decide| J["Approve/Reject/Hold"]
    J -->|Update Status| K["Database"]
    K -->|Final Email| H
    H -->|Verify Email| L["Tracking Portal"]
    L -->|View Status| M["Timeline & Decision"]
```

### Workflow Steps

1. **Application Submission**
   - Loan Assistant enters applicant data via web form
   - Form validation on frontend and backend
   - Application saved to database with reference ID

2. **ML Prediction**
   - Feature preprocessing (scaling, encoding)
   - XGBoost model inference
   - Confidence score, risk score, and risk category calculated

3. **Explanation Generation**
   - AI provider (Gemini/Hugging Face) generates explanation
   - Fallback to rule-based explanations if API fails
   - Financial analysis and recommendations included

4. **Admin Review**
   - Application appears in Credit Manager dashboard
   - Manager reviews ML decision and AI explanation
   - Manager approves, rejects, or holds application
   - Optional manager remarks added for audit

5. **Applicant Notification**
   - Email sent to applicant with decision and explanation
   - Verification code for tracking portal access
   - Email includes smart tips for future applications

6. **Tracking**
   - Applicant verifies email and accesses tracking portal
   - Views real-time application status
   - Reviews decision timeline and all event history

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution**: Ensure virtual environment is activated and requirements installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: Database file not found
**Solution**: Database is auto-created on first run. If missing, reset it:
```bash
rm instance/CreditLens.db  # Remove old database
python -c "from app import create_app; app = create_app()"  # Recreate
```

### Issue: "ConnectionRefusedError" when sending emails
**Solution**: Check SMTP configuration in `.env`. For Gmail, ensure:
- 2-Step Verification is enabled
- App-specific password is used (not regular Gmail password)
- `EMAIL_PORT=465` with `EMAIL_USE_SSL=True`

### Issue: "API key not configured" for Gemini/Hugging Face
**Solution**: Add API keys to `.env`:
```env
GEMINI_API_KEY=your-key
HUGGINGFACEHUB_API_TOKEN=your-token
```
Or set `NLP_PROVIDER=none` for rule-based explanations only.

### Issue: Login fails with demo credentials
**Solution**: Reset database:
```bash
rm instance/CreditLens.db
python -c "from app import create_app; app = create_app()"
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

This project is open-source. Please check the repository for license details.

---

## 👨‍💻 Author

**Praveen Soni**  
GitHub: [@praveen-soni06](https://github.com/praveen-soni06)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Support

For issues, questions, or suggestions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review existing [GitHub Issues](https://github.com/praveen-soni06/CreditLens--ML-Based-Loan-Analyzer-/issues)
3. Create a new issue with detailed description

---

## ⭐ Acknowledgments

- XGBoost for the powerful ML framework
- Flask for the lightweight web framework
- Scikit-Learn for ML utilities
- Google Gemini and Hugging Face for AI capabilities
- The open-source community for amazing tools

---

**Last Updated**: July 2026  
**Version**: 1.0.0
