# Changelog

All notable changes to CreditLens will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-20

### Added

#### Core Features
- **ML Prediction Engine** – XGBoost-based loan approval classification
- **Web Interface** – Flask-based responsive UI with Bootstrap styling
- **Multi-Role Authentication** – Session-based auth for credit managers and loan assistants
- **Admin Dashboard** – Real-time metrics, application filtering, decision management
- **AI Explanations** – Google Gemini and Hugging Face integration for natural language decision explanations
- **Email Notifications** – Automated applicant communications with SMTP support
- **Application Tracking** – Public portal for applicants to monitor loan status
- **Risk Scoring** – Multi-factor risk assessment with Low/Medium/High categorization
- **SQLite Persistence** – Full relational database with SQLAlchemy ORM

#### Database & Models
- User management with role-based access control
- Application storage with comprehensive applicant data
- Prediction tracking with confidence and risk scores
- Email verification system with OTP codes
- AI explanation storage with provider metadata
- Application timeline events for audit logging

#### Routes & Endpoints
- `/login` – User authentication
- `/application` – Loan application form
- `/submit-application` – ML prediction endpoint
- `/dashboard` – Credit manager dashboard
- `/dashboard/review` – Decision submission
- `/track` – Applicant tracking portal
- `/result/<ref_id>` – Prediction results page

#### Configuration
- Environment variable support via python-dotenv
- Flexible AI provider selection (Gemini, Hugging Face, rule-based)
- Configurable SMTP settings
- Demo user seeding on first run

#### Documentation
- Comprehensive README with installation, usage, and API docs
- Database schema documentation
- ML model training notebook
- Architecture overview

### Fixed
- Initial project release

### Known Issues
- Screenshots placeholders in README (add to `docs/images/`)
- Demo credentials in production (change in production deployment)
- Email template customization options limited
- No multi-language support yet

---

## [Unreleased]

### Planned Features

#### Model Improvements
- [ ] Hyperparameter optimization for XGBoost
- [ ] Feature importance analysis
- [ ] Model versioning system
- [ ] A/B testing framework for model variants
- [ ] Ensemble methods (Random Forest, Gradient Boosting)

#### User Experience
- [ ] Mobile-responsive dashboard
- [ ] Dark mode theme
- [ ] Bulk application upload (CSV)
- [ ] Export reports (PDF, Excel)
- [ ] Advanced filtering and search
- [ ] Application comparison view

#### Email & Notifications
- [ ] SMS notifications
- [ ] Push notifications
- [ ] Email template customization UI
- [ ] Scheduled reminder emails
- [ ] Webhook support

#### Security
- [ ] Two-factor authentication (2FA)
- [ ] API key management
- [ ] Audit log encryption
- [ ] Rate limiting
- [ ] CORS configuration
- [ ] SQL injection prevention hardening

#### Analytics & Reporting
- [ ] Advanced dashboard analytics
- [ ] Approval trend analysis
- [ ] Default rate predictions
- [ ] Demographic insights
- [ ] Export monthly/yearly reports
- [ ] Real-time metrics WebSocket

#### Internationalization
- [ ] Multi-language UI support
- [ ] Localized email templates
- [ ] Currency/locale settings
- [ ] Right-to-left language support

#### Deployment
- [ ] Docker containerization
- [ ] Docker Compose setup
- [ ] Kubernetes manifests
- [ ] AWS Lambda deployment
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Automated testing
- [ ] Performance monitoring

#### Database
- [ ] PostgreSQL support (production)
- [ ] Database migration system
- [ ] Backup/restore utilities
- [ ] Data archival system

#### API
- [ ] REST API documentation (Swagger/OpenAPI)
- [ ] GraphQL support
- [ ] API authentication (JWT, OAuth2)
- [ ] Rate limiting per user
- [ ] Webhook subscriptions

---

## Version History

### 1.0.0 (Current)
- Initial release
- XGBoost ML model
- Flask web interface
- Multi-role authentication
- Email notifications
- Application tracking
- Risk scoring
- SQLite database

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting issues and submitting pull requests.

---

## Support

For questions or issues:
1. Check [README Troubleshooting](README.md#-troubleshooting)
2. Review [GitHub Issues](https://github.com/praveen-soni06/CreditLens--ML-Based-Loan-Analyzer-/issues)
3. Create a new issue with detailed information

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.
