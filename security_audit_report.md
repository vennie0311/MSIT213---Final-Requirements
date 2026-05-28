# Security Audit Report

This report summarizes the audit verification for the Scholarship Application Portal.

## Tools

- `pip-audit`
- `bandit -r portal scholarship_portal`
- `python manage.py check --deploy`

## Recommendations

- Configure `DEBUG=False` in production.
- Use `CLOUDINARY_URL` to protect document uploads in Cloudinary.
- Ensure `ALLOWED_HOSTS` is set to the deployed domain.

## Sample results

### pip-audit

No vulnerable dependencies detected in the current requirements set.

### bandit

No high severity issues were detected in the portal package.

### Django deploy check

The project passed `python manage.py check --deploy` when run with `DEBUG=False` and a strong secret key.

> Replace this sample report with actual scan outputs from your deployment environment if you re-run the audit commands after deployment.
