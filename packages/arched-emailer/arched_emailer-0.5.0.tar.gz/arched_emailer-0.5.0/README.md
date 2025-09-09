# Arched Emailer

<!-- coverage-badge -->

![Coverage](badges/coverage.svg) 91.6%

<!-- coverage-badge-end -->


### A simple emailer for sending emails / error logs to a list of recipients.

## Ignoring URL Patterns (Flask)

ArchedEmailer ignores common noise endpoints by default when intercepting Flask errors.

- Default ignored patterns:
  - `^/static(?:/.*)?$` (Flask static files)
  - `^/favicon\.ico$`, `^/robots\.txt$`
  - `^/.*\.(css|js|png|jpg|jpeg|gif|svg|ico|webp|map)$` (static assets by extension)
  - `^/(health|healthz|ready|live|status)$` (health/ready endpoints)

Override the patterns via environment variable or programmatically:

- Env override (`ARCHED_IGNORE_URL_PATTERNS`):
  - Comma‑separated: `^/api/metrics$,^/static/.*$`
  - JSON array: `["^/api/metrics$", "^/static/.*$"]`

- Programmatic:
  ```python
  ae.init_app(app, intercept_errors=True, ignore_url_patterns=[r"^/health$", r"^/static/.*$"])
  ```

Explicit `ignore_url_patterns` passed to `init_app` takes precedence over the env var; if neither is provided, defaults apply.

## Formatting & Linting

This repo uses Black and Ruff, integrated via pre-commit.

- Setup hooks: `pre-commit install`
- Run on all files: `pre-commit run --all-files`
- Manual format: `black .` and `ruff check . --fix` (optional `ruff format .`)

Configuration lives in `pyproject.toml` and `.pre-commit-config.yaml`.

## Change Log

- v0.1.4 (05/02/2024)
    - Changed requirements to match the latest version of `smtpymailer` which now uses data attributes to convert images
      to CID or base64, rather than the old method of using a method parameter which was rather clunky.
    - Added customer ID which will enable me to log requests server side per customer, and giving each customer their
      own unique API key
    - Changed the `send_email` method, so we can send emails not only from `Arched` but also from the customer's email
      address if needed. This will be useful for sending emails from the customer's email address, but using `Arched`'s
      SMTP server. 

- v0.1.5 (06/02/2024)
  - Make `_get_email_path` one function instead of two. 
  - Added a `_make_request` function that can be used for all db calls.
  - Changed the requirements for the class init. Most of the needed data is stored on the server now, with a fallback
    mechanism to fetch from file if the server is down.
  - Added a method to send errors/success logs to the backend. This will be useful for keeping track of errors. 
  - Created a decorator which can wrap functions around a try/except block, and send the error or success email and log
    to the backend.

- v0.1.6 (07/02/2024)
  - Changed the lookup `api_key` and `customer_id` method
  
- v0.1.7 (07/02/2024)
  - Quick fix to re-add the error text to the `send_error_email` function. I've realised that it would be useful to have
    in some cases.
  
- v0.1.8 (07/02/2024)
  - Made it flask proof with an `init_app` method

- v0.2.0 (07/02/2024)
  - Major update to all, fully working with arched.dev backend. Updating correctly. 

- v0.2.1 (07/02/2024)
  - Minjor bug fixes

- v0.2.2 (08/02/2024)
  - Changes to the flask `init_app` and how it intercepts exceptions.
  - Changes to the UUID that was being generated before, was too long. 

- v0.2.3 (09/02/2024)
  - Added a clause that removes `request` from the globals() and locals() calls as it was causing a flask context 
    error.
  - 
- v0.2.4 (09/02/2024)
  - Had need to report success to the backend without emailing so added `update_db_only` to the `send_success_email` 
    method.

- v0.2.5 (09/02/2024)
  - Minor bug fix for the class setup. Wasn't correctly reading the mail_connection details from the local dir
    when the server was down.

- v0.2.6 (09/02/2024)
  - Oops, another, minor bug fix. Wasn't correctly reading the mail_connection details from the local dir
    when the server was down.

- v0.2.7 (09/02/2024)
  - Changed how it reports the HTML content to the backend, it was sending blank strings. Now it correctly gets the html from the `text/html` multipart of the email object.

- v0.2.8 (09/02/2024)
  - Missed the success send email function

- v0.2.9, 0.2.10, 0.2.11, 0.2.12, 0.2.13 (10/02/2024)
  - Minor bug fixes
  - Dependency issues

- v0.2.15 (11/02/2024)
  - added the option to pass in to the `init_app` method, the `current_user` from flask-login. Then error messages will
    be sent with the user's email address or other details.

- v0.2.15,16,17,18 (11/02/2024)
  - added the option to pass in to the `init_app` method a flag whether to use `current_user` from flask-login. Then error messages will
    be sent with the user's email address or other details.

- v0.2.19,20,21 (11/02/2024)
  - Added a `before_request` handler that will add last few urls visited by the user to the error message.
  - Minor bug fixes
  
- v0.2.23 (12/02/2024)
  - Changes to the way html_content is gathered 
  - Issue with flask context when not a flask app bug

- v0.2.24 (12/02/2024)
  - Issue with post requests being sent to raw ip. Most likely bots. Causing error when I'm not interested.

- v0.2.25 (20/02/2024)
    - Minor bug fixes for flask init_app and error handling 
- v0.2.26 (20/02/2024)
    - Requirements update
- v0.2.34 (20/02/2024)
    - Added log message to the class so the database can accept logs.
