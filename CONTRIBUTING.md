# Contributing to CreditLens

Thank you for your interest in contributing to CreditLens! We welcome contributions from the community and appreciate your help in making this project better.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others succeed

## How to Contribute

### Reporting Bugs

1. **Check existing issues** – Search to see if the bug has been reported
2. **Provide details:**
   - Python version and OS
   - Steps to reproduce
   - Expected vs. actual behavior
   - Error logs or stack trace
   - Screenshots (if applicable)
3. **Use a clear title** – Be specific about the issue

### Suggesting Features

1. **Check existing issues** – Avoid duplicates
2. **Describe the feature:**
   - What problem does it solve?
   - How would you use it?
   - Any potential implementation approaches
3. **Provide examples** – Show use cases or mockups

### Submitting Pull Requests

#### Setup Development Environment

```bash
# Clone and setup
git clone https://github.com/praveen-soni06/CreditLens--ML-Based-Loan-Analyzer-.git
cd CreditLens--ML-Based-Loan-Analyzer-
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive names:
- `feature/add-prediction-confidence-threshold`
- `fix/email-verification-timeout`
- `docs/database-schema-documentation`

#### Make Your Changes

1. **Follow Python conventions:**
   - PEP 8 style guide
   - 4-space indentation
   - Descriptive variable names
   - Add docstrings to functions

2. **Test your changes:**
   ```bash
   python run.py
   ```
   - Manually test affected features
   - Test with different user roles if applicable
   - Verify database operations

3. **Update documentation:**
   - Update README if adding features
   - Add docstrings to new functions
   - Document configuration changes

#### Commit Guidelines

```bash
git add .
git commit -m "feature: add loan amount validation"
git commit -m "fix: correct email verification timeout logic"
git commit -m "docs: update installation instructions"
```

**Commit message format:**
- Start with type: `feature:`, `fix:`, `docs:`, `refactor:`, `test:`
- Use lowercase
- Be specific and concise
- Reference issues: `fix: resolve #123`

#### Push and Create PR

```bash
git push origin feature/your-feature-name
```

1. Go to GitHub and create a Pull Request
2. **Fill in the PR template:**
   - Title: `Add feature X` or `Fix issue with Y`
   - Description: What changed and why
   - Link related issues: `Closes #123`
3. **Add labels:** feature, bug, enhancement, documentation, etc.

### Code Review Process

1. **Automated checks** – CI/CD pipeline verifies code
2. **Manual review** – Maintainers review for:
   - Code quality and style
   - Test coverage
   - Documentation completeness
   - Security implications
3. **Feedback** – Address review comments
4. **Approval & Merge** – Maintainer approves and merges

## Development Areas

### Areas We Need Help With

- **ML Model Improvement** – Better training, hyperparameter tuning
- **Frontend UI/UX** – Responsive design, accessibility
- **Email Templates** – Better formatted decision notifications
- **Documentation** – Guides, tutorials, API documentation
- **Testing** – Unit tests, integration tests
- **Deployment** – Docker, AWS, GCP setup guides
- **Internationalization** – Multi-language support

### Getting Started (Difficulty Levels)

**Beginner:**
- Fix typos in documentation
- Improve error messages
- Add helpful comments
- Create issue templates

**Intermediate:**
- Add validation to forms
- Improve email templates
- Add new configuration options
- Write utility functions

**Advanced:**
- Implement new ML models
- Refactor database layer
- Add new API endpoints
- Improve security measures

## File Structure for Changes

```
app/
├── routes/          # API endpoints (POST/GET handlers)
├── templates/       # HTML templates
├── static/          # CSS, JavaScript
├── utils/           # Helper functions (email, NLP, lifecycle)
└── database/        # SQLAlchemy models

ML/
├── loan_data.csv    # Training data
├── model.pkl        # XGBoost model
└── scaler.pkl       # Feature scaler

notebooks/
└── training.ipynb   # Model training notebook
```

## Important Considerations

### Database Changes

If modifying database models in `app/database/db.py`:
1. Update model class definition
2. Test database creation/migration
3. Document schema changes in README
4. Update database section in README

### ML Model Changes

If retraining the model:
1. Update `notebooks/training.ipynb`
2. Regenerate and commit `ML/model.pkl` and `ML/scaler.pkl`
3. Document model performance in commit message
4. Update ML section in README with new metrics

### Configuration Changes

If adding new environment variables:
1. Add to `.env.example`
2. Update `.env` handling in `app/__init__.py`
3. Document in README's Environment Variables section
4. Provide sensible defaults

### Email Templates

Email templates are in `app/templates/emails/`:
- Keep design responsive
- Include support contact info
- Test with different email clients

## Testing Before Submission

```bash
# 1. Run the application
python run.py

# 2. Test core functionality
# - Login as admin and assistant
# - Submit application
# - Review and approve/reject
# - Check email notifications
# - Test tracking portal

# 3. Test edge cases
# - Invalid form inputs
# - Missing database
# - SMTP connection failure
# - API timeouts (if using external APIs)

# 4. Database check
# - Verify new data persists
# - Check relationships are correct
# - Ensure no duplicate data
```

## Documentation Standards

### Docstring Format

```python
def submit_application(data):
    """
    Submit a new loan application and generate ML prediction.
    
    Args:
        data (dict): Application data with keys:
            - customer_name (str): Applicant name
            - person_age (int): Age in years
            - credit_score (int): FICO score
            - loan_amnt (float): Requested amount
    
    Returns:
        dict: Prediction result with keys:
            - reference_id (str): Unique application reference
            - prediction (str): 'Approved' or 'Rejected'
            - confidence (float): 0.0-1.0 confidence score
    
    Raises:
        ValueError: If required fields are missing
        Exception: If ML model fails to load
    """
```

### README Updates

When adding features, update README sections:
- **Tech Stack** – New dependencies
- **Key Features** – New capabilities
- **Project Structure** – New files/directories
- **Usage** – How to use new feature
- **API Endpoints** – New routes
- **Configuration** – New env variables
- **Database** – New tables/fields

## Community

- **GitHub Issues** – Report bugs and request features
- **Discussions** – Ask questions, share ideas
- **Pull Requests** – Submit code changes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Check the [README](README.md) for documentation
- Review existing [Issues](https://github.com/praveen-soni06/CreditLens--ML-Based-Loan-Analyzer-/issues)
- Check [Troubleshooting](README.md#-troubleshooting) section

---

Thank you for contributing to CreditLens! 🎉
