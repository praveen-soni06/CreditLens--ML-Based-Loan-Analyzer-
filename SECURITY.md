# Security Policy

## Reporting Security Vulnerabilities

**DO NOT** open a public GitHub issue for security vulnerabilities. Instead, please email security concerns to:

**Email:** [Contact repository owner privately]

Please include:
- Type of vulnerability
- Location (file path, line number)
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

We will acknowledge your report within 48 hours and work with you to develop and deploy a fix.

## Security Best Practices

### For Deployment

1. **Environment Variables**
   - Store all secrets in `.env` files (never commit)
   - Use strong, randomly generated `SECRET_KEY`
   - Rotate API keys regularly
   - Use app-specific passwords (not user passwords)

2. **Database**
   - Use PostgreSQL in production (not SQLite)
   - Enable SSL connections
   - Backup database regularly
   - Restrict database user permissions

3. **Email Configuration**
   - Use app-specific passwords (Gmail)
   - Enable SSL/TLS (EMAIL_USE_SSL=True)
   - Validate email addresses
   - Monitor for unauthorized email sending

4. **API Keys**
   - Store Gemini and Hugging Face keys securely
   - Rotate keys periodically
   - Use separate keys for dev/prod
   - Monitor API usage for anomalies

### For Users

1. **Password Management**
   - Use strong, unique passwords
   - Change default demo credentials immediately
   - Enable any multi-factor authentication if available
   - Never share credentials

2. **Data Protection**
   - Verify applicant email addresses
   - Protect sensitive financial data
   - Use HTTPS in production
   - Implement proper access controls

### Code Security

1. **Input Validation**
   - Validate all form inputs
   - Sanitize user data
   - Prevent SQL injection (SQLAlchemy ORM prevents most cases)
   - Validate file uploads

2. **Authentication & Authorization**
   - Check user roles for sensitive operations
   - Implement proper session management
   - Logout inactive sessions
   - Prevent unauthorized access

3. **Data Handling**
   - Don't log sensitive information (passwords, API keys)
   - Use HTTPS for all data transmission
   - Encrypt sensitive fields if needed
   - Implement proper error handling (don't expose stack traces)

4. **Dependencies**
   - Keep dependencies up to date
   - Use `pip audit` to check for vulnerabilities
   - Monitor security advisories
   - Review dependency licenses

## Vulnerability Management

- **Critical**: Address within 24 hours
- **High**: Address within 1 week
- **Medium**: Address within 2 weeks
- **Low**: Address within 1 month

## Security Testing

Before deployment, ensure:

```bash
# Check for known vulnerabilities in dependencies
pip audit

# Review for common security issues
# - Check for hardcoded secrets
# - Verify input validation
# - Check authentication/authorization
# - Review error handling

# Test with admin and assistant roles
# - Verify access control works
# - Check for privilege escalation
# - Test data isolation
```

## Common Vulnerabilities & Mitigations

### SQL Injection
- **Mitigation**: Using SQLAlchemy ORM prevents most attacks
- **Action**: Always use ORM queries, never raw SQL

### Cross-Site Scripting (XSS)
- **Mitigation**: Jinja2 auto-escapes HTML by default
- **Action**: Validate and sanitize user input in templates

### Cross-Site Request Forgery (CSRF)
- **Mitigation**: Implement CSRF tokens in forms
- **Action**: Use Flask-WTF or similar for form protection

### Weak Passwords
- **Mitigation**: Enforce strong password requirements
- **Action**: Implement password strength validation

### Unencrypted Transmission
- **Mitigation**: Use HTTPS/TLS in production
- **Action**: Set secure cookies, validate certificates

### Exposed Credentials
- **Mitigation**: Use environment variables, never commit secrets
- **Action**: Use `.gitignore`, rotate compromised keys

## Production Checklist

- [ ] All environment variables configured
- [ ] SECRET_KEY is strong and unique
- [ ] Database is PostgreSQL or secured SQLite
- [ ] HTTPS/SSL is enabled
- [ ] CORS is properly configured
- [ ] Rate limiting is implemented
- [ ] Input validation is comprehensive
- [ ] Logging doesn't expose sensitive data
- [ ] Backups are automated and tested
- [ ] Monitoring and alerting is configured
- [ ] Access logs are retained
- [ ] Dependencies are up to date
- [ ] Security headers are configured
- [ ] Error pages don't expose system info

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security](https://flask.palletsprojects.com/en/latest/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/20/faq/security.html)
- [Python Security](https://python.readthedocs.io/en/latest/library/security_warnings.html)

## Change Log

### Changes to Security Policy
Document any updates to security practices here.

---

Thank you for helping keep CreditLens secure! 🔒
