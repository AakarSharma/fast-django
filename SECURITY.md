# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in fast-django, please follow these steps:

### 1. Do NOT create a public GitHub issue

**Do not** create a public GitHub issue for security vulnerabilities. This could potentially expose the vulnerability to malicious actors before we have a chance to fix it.

### 2. Report privately

Please report security vulnerabilities privately by:

- **Email**: Send details to [security@fast-django.dev](mailto:security@fast-django.dev)
- **GitHub Security Advisory**: Use GitHub's private vulnerability reporting feature
- **Direct Message**: Contact maintainers directly through GitHub

### 3. Include the following information

When reporting a vulnerability, please include:

- **Description**: A clear description of the vulnerability
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Impact**: Potential impact and severity assessment
- **Environment**: OS, Python version, fast-django version, and other relevant details
- **Proof of Concept**: If possible, include a minimal proof of concept
- **Suggested Fix**: If you have ideas for fixing the issue

### 4. Response Timeline

We will respond to security reports within:

- **Initial Response**: 24-48 hours
- **Status Update**: Within 1 week
- **Resolution**: As quickly as possible, typically within 30 days

### 5. Disclosure Process

- We will acknowledge receipt of your report within 24-48 hours
- We will investigate the issue and provide regular updates
- We will work with you to understand and resolve the issue
- We will coordinate the disclosure timeline with you
- We will credit you in our security advisories (unless you prefer to remain anonymous)

## Security Best Practices

### For Users

1. **Keep fast-django updated** - Always use the latest version
2. **Review dependencies** - Regularly update your project dependencies
3. **Use environment variables** - Store sensitive configuration in environment variables
4. **Validate input** - Always validate and sanitize user input
5. **Use HTTPS** - Always use HTTPS in production
6. **Secure your database** - Use strong database credentials and connections
7. **Regular backups** - Maintain regular backups of your data
8. **Monitor logs** - Monitor application logs for suspicious activity

### For Developers

1. **Follow secure coding practices** - Use secure coding guidelines
2. **Input validation** - Always validate and sanitize input
3. **Authentication** - Implement proper authentication and authorization
4. **Secrets management** - Never commit secrets to version control
5. **Dependency management** - Keep dependencies updated and scan for vulnerabilities
6. **Code review** - Always review code for security issues
7. **Testing** - Include security testing in your test suite

## Security Features

fast-django includes several security features:

- **Type Safety**: Full type hints help prevent runtime errors
- **Input Validation**: Pydantic models provide automatic input validation
- **Settings Security**: Environment-based configuration prevents hardcoded secrets
- **Admin Security**: Admin interface includes authentication and authorization
- **SQL Injection Protection**: ORM provides protection against SQL injection
- **CSRF Protection**: Built-in CSRF protection through FastAPI
- **CORS Support**: Configurable CORS settings for API security

## Known Security Considerations

### Database Security

- Use strong database credentials
- Enable SSL/TLS for database connections
- Regularly update database software
- Use connection pooling appropriately
- Implement proper backup and recovery procedures

### API Security

- Implement rate limiting for API endpoints
- Use proper authentication and authorization
- Validate all input data
- Implement proper error handling
- Use HTTPS in production
- Consider API versioning for security updates

### Admin Interface Security

- Use strong passwords for admin users
- Implement two-factor authentication if possible
- Restrict admin access to trusted IP addresses
- Regularly audit admin user accounts
- Monitor admin access logs

## Security Updates

Security updates will be released as:

- **Patch releases** (e.g., 0.1.1) for critical security fixes
- **Minor releases** (e.g., 0.2.0) for security improvements
- **Major releases** (e.g., 1.0.0) for significant security changes

## Security Advisories

Security advisories will be published:

- On GitHub Security Advisories
- In the project's CHANGELOG.md
- Via project announcements
- Through the project's communication channels

## Contact

For security-related questions or concerns:

- **Email**: [security@fast-django.dev](mailto:security@fast-django.dev)
- **GitHub**: [Create a private security advisory](https://github.com/AakarSharma/fast-django/security/advisories/new)
- **Issues**: Use GitHub Issues for non-security related questions

## Acknowledgments

We thank all security researchers and community members who help keep fast-django secure by responsibly reporting vulnerabilities.

## License

This security policy is part of the fast-django project and is subject to the same MIT License as the project.
