# Security Policy

## Supported Versions

We support the following versions of Coffee Script with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in Coffee Script, please report it to us in a responsible manner.

### How to Report

1. **Do NOT create a public GitHub issue** for security vulnerabilities
2. Send an email to [security@example.com] with:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Any suggested fixes (optional)

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 5 business days
- **Regular Updates**: We will send updates on our progress every 7 days until the issue is resolved
- **Resolution Timeline**: We aim to resolve critical vulnerabilities within 30 days

### Our Commitment

- We will work with you to understand and resolve the issue quickly
- We will keep you informed throughout the process
- We will credit you in our security advisory (unless you prefer to remain anonymous)
- We will not take legal action against you if you follow responsible disclosure practices

## Security Best Practices

When using Coffee Script:

1. **Keep Dependencies Updated**: Regularly update all dependencies using `pip install --upgrade`
2. **Use Virtual Environments**: Always run Coffee Script in isolated Python environments
3. **Monitor System Resources**: Be aware that Coffee Script monitors system information
4. **Review Permissions**: Ensure Coffee Script has only necessary system permissions
5. **Regular Updates**: Keep Coffee Script updated to the latest version

## Scope

This security policy applies to:

- The main Coffee Script application (`src/coffee/`)
- Build and deployment scripts
- Dependencies listed in `pyproject.toml`
- CI/CD workflows and configurations

## Out of Scope

The following are outside the scope of this security policy:

- Vulnerabilities in third-party dependencies (report to respective maintainers)
- Issues in development/testing environments
- Social engineering attacks
- Physical access attacks

## Security Features

Coffee Script implements the following security measures:

1. **Input Validation**: All system command inputs are validated and sanitized
2. **Minimal Privileges**: The application requests only necessary system permissions
3. **Secure Dependencies**: We regularly audit and update all dependencies
4. **Code Analysis**: Automated security scanning via Bandit and pip-audit in CI/CD
5. **Type Safety**: Comprehensive type annotations help prevent runtime errors

## Contact

For security-related questions or concerns:

- Email: [security@example.com]
- Security Advisory: [GitHub Security Advisories](https://github.com/bhaskarbhaumik/coffee/security/advisories)

Thank you for helping keep Coffee Script secure!