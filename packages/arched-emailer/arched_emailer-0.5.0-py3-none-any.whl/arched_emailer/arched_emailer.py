import base64
import datetime
from email.mime.multipart import MIMEMultipart
import json
import logging
import os
from pathlib import Path
import re
import tempfile
import threading
import traceback
import types
from typing import Any, Callable, Dict, Optional, Tuple, Union

from flask import Flask, abort, render_template, session
import requests

try:  # Safe import for rotating handler; fallback to basic file handler in tests
    from concurrent_log_handler import ConcurrentRotatingFileHandler
except Exception:  # pragma: no cover - exercised when dependency missing

    class ConcurrentRotatingFileHandler(logging.FileHandler):  # type: ignore
        def __init__(self, filename, maxBytes=None, backupCount=None):  # noqa: N803
            super().__init__(filename)


try:  # Safe import for mailer; fallback stub for test environments
    from smtpymailer import SmtpMailer
except Exception:  # pragma: no cover - exercised when dependency missing

    class _FakeSender:
        def __init__(self, email: str):
            self.email = email

    class SmtpMailer:  # type: ignore
        def __init__(self, sender_email: str, sender_name: Optional[str] = None):
            self.sender = _FakeSender(sender_email)
            self.message = None

        def send_email(self, *args, **kwargs):
            self.message = types.SimpleNamespace()
            return True


from werkzeug.exceptions import HTTPException, default_exceptions

from arched_emailer.encryption import (
    generate_random_string,
    obfuscate_sensitive_info,
    redact_text,
)

__version__ = "0.5.0"

BASE_URL = "https://arched.dev"


class ArchedEmailer:
    """
    A class for sending emails.
    ARCHED.DEV
    """

    error_log: dict
    app_name: str = "ArchedErrors"
    app_author: str = "Arched"
    error_sender: str = "errors@arched.dev"
    error_sender_name: str = "Arched Errors"
    success_sender: str = "success@arched.dev"
    success_sender_name: str = "Arched Notifications"
    errors_name_time: dict = dict()
    connection_details: str
    arched_api_key: str
    temp_app: Optional[str] = None
    time_start: Optional[datetime.datetime] = None
    app: Optional[str] = None
    flask_app: Optional["Flask"] = None
    mailer: Optional[SmtpMailer] = None
    success_mailer: Optional[SmtpMailer] = None
    task_id: Optional[int] = None
    current_user = None
    arched_api_key = None
    _lock = threading.Lock()
    logger = None  # Placeholder for the logger
    bot_non_flask_error_count: int = 0
    # Default URL patterns to ignore for error processing
    DEFAULT_IGNORE_URL_PATTERNS = [
        r"^/static(?:/.*)?$",  # Flask static files
        r"^/favicon\.ico$",  # Favicon
        r"^/robots\.txt$",  # Robots file
        r"^/.*\.(?:css|js|png|jpg|jpeg|gif|svg|ico|webp|map)$",  # Static assets by extension
        r"^/(?:health|healthz|ready|live|status)$",  # Health/ready endpoints
    ]

    def __init__(
        self,
        app: str,
        api_key: Optional[str] = None,
        mail_connection_string: Optional[str] = None,
        task_id: Optional[int] = None,
        flask: Optional[bool] = False,
        log_path: Optional[str] = None,
    ) -> None:
        """
        Initialize the ArchedEmailer instance.
        """
        self.error_templates = None
        self.app = app
        self.task_id = task_id
        self.log_path = log_path
        # Initialize logger first
        self._initialize_logger()
        self.log("info", "Initializing ArchedEmailer instance.")

        # Now load the error log
        self.errors_name_time = self._load_error_log()  # Load existing error log

        if not flask:
            self.setup(api_key, mail_connection_string)
        else:
            self.log("debug", "Flask integration enabled; skipping setup.")

        self._cleanup_error_log()

    def _initialize_logger(self) -> None:
        """
        Initializes the rotating file logger but does NOT log to console to avoid interfering with Flask.
        """
        if hasattr(self, "log_path") and self.log_path:
            log_file = self.log_path
            if not os.path.exists(os.path.dirname(log_file)):
                os.makedirs(os.path.dirname(log_file))
        else:
            data_dir = self._get_create_data_dir()
            log_file = os.path.join(data_dir, "arched_emailer.log")

        if not hasattr(self, "logger") or self.logger is None:
            self.logger = logging.getLogger(self.app_name + "_arched")
            self.logger.propagate = False
            self.logger.setLevel(logging.DEBUG)

            # Rotating File Handler

            file_handler = ConcurrentRotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,  # 5 MB
                backupCount=5,
            )
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

            # Do NOT add console handler
            # console_handler = logging.StreamHandler(sys.stderr)  # <--- REMOVE THIS

        self.log("debug", f"Logger initialized with log file: {log_file}")

    def log(self, status_type: str, text: str, exc_info: Optional[bool] = False) -> None:
        """
        Logs a message using the class's logger if it exists.

        Args:
            status_type (str): The severity level of the log (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL").
            text (str): The message to log.
            exc_info (bool, optional): If True, include exception traceback information. Defaults to False.
        """
        if self.logger:
            # Normalize the status_type to uppercase to ensure consistency
            status_type = status_type.upper()

            # Mapping of status_type to logger methods
            log_methods = {
                "DEBUG": self.logger.debug,
                "INFO": self.logger.info,
                "WARNING": self.logger.warning,
                "ERROR": self.logger.error,
                "CRITICAL": self.logger.critical,
            }

            # Get the logging method based on status_type
            log_method = log_methods.get(status_type.upper())

            if log_method:
                # Redact PII/secrets from logs to prevent leakage
                log_method(redact_text(text), exc_info=exc_info)
            else:
                # If an invalid status_type is provided, default to INFO and log a warning
                self.logger.warning(
                    f"Invalid log level '{status_type}' provided. Defaulting to 'INFO'. Message: {redact_text(text)}"
                )
                self.logger.info(redact_text(text), exc_info=exc_info)
        else:
            # Fallback if logger is not initialized
            # You can choose to print to stdout/stderr or silently pass
            # Here, we'll print to stderr
            import sys

            print(f"{status_type}: {redact_text(text)}", file=sys.stderr)
            if exc_info:
                import traceback

                traceback.print_exc(file=sys.stderr)

    def setup(
        self,
        api_key: Optional[str] = None,
        mail_connection_string: Optional[str] = None,
    ) -> None:
        """
        Set up the ArchedEmailer instance.

        Args:
            api_key (str, optional): The API key for the Arched API.
            mail_connection_string (str, optional): The connection string for the mail server.

        Returns:
            None
        """
        self.log("info", "Setting up ArchedEmailer.")
        self.arched_api_key = os.getenv("ARCHED_API_KEY") or api_key
        self.connection_details = os.getenv("MAIL_CONNECTION_STRING") or mail_connection_string

        self.log("debug", f"Arched API Key: {'***' if self.arched_api_key else 'None'}")
        self.log(
            "debug",
            f"Mail Connection Details: {'***' if self.connection_details else 'None'}",
        )

        self._get_set_user_details()
        self._load_env()

        try:
            self.mailer = SmtpMailer(self.error_sender, self.error_sender_name)
            self.success_mailer = SmtpMailer(self.success_sender, self.success_sender_name)
            self.log("info", "SMTP mailers initialized successfully.")
        except Exception:
            self.log("error", "Failed to initialize SMTP mailers.", exc_info=True)

    def init_app(
        self,
        app: "Flask",
        intercept_errors: Optional[bool] = True,
        add_current_user: bool = True,
        ignore_url_patterns: Optional[list[str]] = None,
        error_templates: Optional[Dict[int, str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the application with the ArchedEmailer instance.

        Args:
            app: The Flask application instance.
            intercept_errors (bool, optional): Whether to intercept errors and send emails. Default is True.
            add_current_user (bool, optional): Whether to use the current user for the error details. Default is True.
            ignore_url_patterns (list, optional): A list of regex patterns to ignore when sending error emails.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        from flask import request, session

        self._initialize_logger()

        self.log("info", "Initializing Flask application with ArchedEmailer.")
        app.extensions["arched_emailer"] = self
        self.flask_app = app

        self.error_templates = error_templates or {}

        if intercept_errors:
            self.log("debug", "Error interception enabled.")
            # Resolve ignore patterns: explicit arg > env override > defaults
            resolved_patterns: list[str]
            if ignore_url_patterns is not None:
                resolved_patterns = ignore_url_patterns
            else:
                env_val = os.getenv("ARCHED_IGNORE_URL_PATTERNS")
                if env_val:
                    resolved_patterns = self._parse_ignore_patterns_env(env_val)
                else:
                    resolved_patterns = list(self.DEFAULT_IGNORE_URL_PATTERNS)

            self.ignore_url_patterns = resolved_patterns
            self.log("debug", f"Ignoring URL patterns: {resolved_patterns}")

            def format_dict_for_email(data):
                """
                Format a dictionary for use in an email.

                Args:
                    data (dict): The dictionary to be formatted.

                Returns:
                    str: The formatted dictionary.
                """
                return json.dumps(data, indent=4).replace(" ", "&nbsp;").replace("\n", "<br>")

            def update_visited_urls():
                # Initialize the visited URLs list in the session if not present
                if "visited_urls" not in session:
                    session["visited_urls"] = []
                    self.log("debug", "Initialized 'visited_urls' in session.")

                # Get the current URL
                current_url = request.url
                if (
                    "static" not in current_url
                    and ".js" not in current_url
                    and ".css" not in current_url
                ):
                    # Update the session with the current URL, keeping only the last 5 URLs
                    visited_urls = session["visited_urls"]
                    visited_urls.append(current_url)
                    session["visited_urls"] = visited_urls[-5:]  # Keep only the last 5 URLs
                    self.log("debug", f"Updated visited URLs: {session['visited_urls']}")

            @app.before_request
            def before_request():
                """
                A function to run before each request.
                It logs the visited URLs.
                """
                update_visited_urls()

            def raise_error(template, error_code, error_temp):
                # Always preserve the original error_code for the HTTP response
                if template:
                    return render_template(template), error_code
                if error_temp:
                    return render_template(error_temp), error_code
                # Always return a valid response tuple as a last resort
                return f"{error_code} Error", error_code

            # Register a custom error handler for HTTP exceptions
            def handle_http_exception(error):
                request_path = request.path

                from arched_emailer.utils import is_bot

                # Determine the error code
                error_code = error.code if hasattr(error, "code") else 500
                self.log("debug", f"Handling error with code: {error_code}")

                # Check if a custom template exists for this error code
                template = self.error_templates.get(error_code, None)
                error_temp = self.error_templates.get("other", None)

                if is_bot():
                    self.log("debug", "Request identified as bot; skipping error handling.")
                    # Return None so Flask propagates the original exception
                    # and produces the framework-default error response (typically 500).
                    return None

                if hasattr(self, "ignore_url_patterns"):
                    for pattern in self.ignore_url_patterns:
                        self.log("debug", f"Checking URL pattern: {pattern}")
                        if re.match(pattern, request.path):
                            self.log(
                                "debug",
                                f"URL {request.url} matches ignore pattern {pattern}; skipping error handling.",
                            )
                            # For ignored URLs, do not send an email; just render an appropriate response
                            return raise_error(
                                self.error_templates.get(error_code, None),
                                error_code,
                                error_temp,
                            )

                registered_routes = {rule.rule for rule in self.flask_app.url_map.iter_rules()}
                if error_code == 404:
                    if request_path not in registered_routes:
                        self.log(
                            "debug",
                            f"Skipping email for 404 non-existent route: {request_path}",
                        )
                        # Preserve 404 and return custom template if available
                        return raise_error(
                            self.error_templates.get(404, None), 404, error_temp
                        )

                self.log(
                    "debug",
                    f"URL PATH {request.path} URL {request.url} does not match any ignore patterns.",
                )
                self._process_error(error, add_current_user, request)

                return raise_error(template, error_code, error_temp)

            # Register handlers for all HTTP exceptions
            for code in default_exceptions.keys():
                app.register_error_handler(code, handle_http_exception)
                self.log("debug", f"Registered error handler for HTTP status code: {code}")

            # Register a handler for non-HTTP exceptions (to catch 500 errors)
            app.register_error_handler(Exception, handle_http_exception)
            self.log("debug", "Registered error handler for general exceptions.")

        self.setup(kwargs.get("api_key"), kwargs.get("mail_connection_string"))
        self.log("info", "Flask application initialization complete.")

    def _parse_ignore_patterns_env(self, value: str) -> list[str]:
        """
        Parse env var for ignore URL patterns.

        Supports either comma-separated regex strings or a JSON array of strings.
        Trims whitespace and drops empty entries.
        """
        try:
            s = value.strip()
            if s.startswith("[") and s.endswith("]"):
                arr = json.loads(s)
                if isinstance(arr, list):
                    return [str(x).strip() for x in arr if str(x).strip()]
        except Exception:
            # fall through to simple split
            pass
        # default: comma-separated list
        parts = [p.strip() for p in value.split(",")]
        return [p for p in parts if p]

    def _process_error(self, error, add_current_user, request):
        """
        Process the error by sending an error email.

        Args:
            error: The exception object.
            add_current_user (bool): Whether to include current user details.
            request: The Flask request context.

        Returns:
            None
        """
        self.log("debug", "Processing an error to send an email.")

        def format_dict_for_email(data):
            return json.dumps(data, indent=4).replace(" ", "&nbsp;").replace("\n", "<br>")

        try:
            # Default error information
            error_code = 500  # Default to internal server error
            error_description = "Internal Server Error"

            # Check if the error is an HTTPException to extract code and description
            if isinstance(error, HTTPException):
                error_code = error.code
                error_description = error.description

            ip = request.headers.get("X-Forwarded-For", request.remote_addr)
            user_agent = request.headers.get("User-Agent", "Unknown")
            referer = request.headers.get("Referer", "Unknown")
            requested_url = request.url
            requested_path = request.path

            error_text = (
                f"<br><strong style='font-size:larger'>{error_code} Error Occurred</strong><br>"
                f"<strong>Description:</strong> {error_description}<br>"
                f"<strong>IP Address:</strong> {ip}<br>"
                f"<strong>User Agent:</strong> {user_agent}<br>"
                f"<strong>Referer:</strong> {referer}<br>"
                f"<strong>Request URL:</strong> {requested_url}<br>"
                f"<strong>Requested Path:</strong> {requested_path}<br>"
                f"<strong>Method:</strong> {request.method}<br>"
            )

            # Add explicit exception details to reduce confusion when reading the email
            try:
                error_type = type(error).__name__ if error is not None else "Unknown"
                error_msg = redact_text(str(error))
                error_text += (
                    f"<br><strong style='font-size:larger'>Exception Details:</strong><br>"
                    f"<strong>Type:</strong> {error_type}<br>"
                    f"<strong>Message:</strong> {error_msg}<br>"
                )
            except Exception:
                pass

            # Include the last visited URLs
            visited_urls = session.get("visited_urls", [])
            if visited_urls:
                visited_urls.reverse()
                error_text += (
                    f"<br><strong style='font-size:larger'>Last Visited URLs:</strong><br>"
                    f"{'<br>'.join(visited_urls)}<br>"
                )

            if add_current_user:
                from flask_login import current_user

                email = getattr(current_user, "email", None)
                name = getattr(current_user, "name", None)
                user_id = getattr(current_user, "id", None)
                error_text += (
                    f"<br><strong style='font-size:larger'>User Details:</strong><br>"
                    f"{f'Email: {email} - ' if email else ''}"
                    f"{f'Name: {name} - ' if name else ''}"
                    f"{f'ID: {user_id}' if user_id else ''}<br>"
                )

            if (
                request.content_type in ["application/xml", "text/xml"]
            ) and request.method.lower() == "post":
                error_text += f"<br><strong style='font-size:larger'>Request XML:</strong><br>{request.data.decode()}<br>"
            elif request.method.lower() == "post" and request.is_json:
                error_text += f"<br><strong style='font-size:larger'>Request JSON:</strong><br>{format_dict_for_email(request.get_json())}<br>"
            elif request.method.lower() == "post" and request.form:
                error_text += f"<br><strong style='font-size:larger'>Request Form:</strong><br>{format_dict_for_email(request.form.to_dict())}<br>"

            self.send_error_email(
                ["lewis@arched.dev"],
                error_text=error_text,
                exception=error,
                allowed_minutes=60,
            )
            self.log("info", "Error email sent successfully.")
        except Exception:
            # Log the exception in a safe way; avoid recursive error handling
            self.log("error", "Failed to process and send error email.", exc_info=True)

    def _get_error_log_path(self) -> str:
        """
        Returns the path to the error log JSON file.
        """
        data_dir = self._get_create_data_dir()
        return os.path.join(data_dir, "error_log.json")

    def _load_error_log(self) -> Dict[str, datetime.datetime]:
        """
        Loads the error log from a JSON file.

        Returns:
            dict: A dictionary mapping error messages to their last sent timestamp.
        """
        with self._lock:
            error_log_path = self._get_error_log_path()
            if os.path.exists(error_log_path):
                try:
                    with open(error_log_path, "r") as f:
                        data = json.load(f)
                        # Convert timestamp strings back to datetime objects
                        self.log("debug", "Loading existing error log.")
                        return {k: datetime.datetime.fromisoformat(v) for k, v in data.items()}
                except Exception:
                    self.log("error", "Failed to load error log.", exc_info=True)
            self.log("debug", "No existing error log found; initializing empty log.")
            return {}

    def _save_error_log(self) -> None:
        """
        Saves the current error log to a JSON file.
        """
        with self._lock:
            error_log_path = self._get_error_log_path()
            try:
                with open(error_log_path, "w") as f:
                    # Convert datetime objects to ISO format strings for JSON serialization
                    data = {k: v.isoformat() for k, v in self.errors_name_time.items()}
                    json.dump(data, f, indent=4)
                self.log("debug", "Error log saved successfully.")
            except Exception:
                self.log("error", "Failed to save error log.", exc_info=True)

    def _cleanup_error_log(self, max_age_minutes: int = 2880) -> None:  # 2 days
        """
        Cleans up the error log by removing entries older than max_age_minutes.

        Args:
            max_age_minutes (int, optional): Maximum age of log entries in minutes. Defaults to 2880 (2 days).

        Returns:
            None
        """
        self.log("debug", "Starting cleanup of error log.")
        current_time = datetime.datetime.now()
        keys_to_delete = [
            k
            for k, v in self.errors_name_time.items()
            if (current_time - v).total_seconds() / 60 > max_age_minutes
        ]
        if keys_to_delete:
            self.log("info", f"Removing {len(keys_to_delete)} old error log entries.")
            for k in keys_to_delete:
                del self.errors_name_time[k]
            self._save_error_log()
        else:
            self.log("debug", "No old error log entries to remove.")

    def _get_set_user_details(self) -> None:
        """
        Fetches the user details from the API and saves them locally. If the server is down or the data fetch fails,
        it attempts to load the user details from a local file.

        Returns:
            None
        """
        self.log("debug", "Fetching user details from API.")
        if self.connection_details:
            self.log("debug", "Connection details already set; skipping API fetch.")
            return

        try:
            data = self._make_request(f"{BASE_URL}/email/user")

            if data[2] == 200 and data[1]:
                # Server responded successfully, update details
                self.customer_id = data[1].get("id")
                if not self.connection_details:
                    self.connection_details = data[1].get("connection_string")

                self.log("info", "User details fetched from API successfully.")
                # Save these details locally as a fallback
                self._save_user_details_locally(data[1])
            else:
                self.log(
                    "warning",
                    "API did not return user details; attempting to load locally.",
                )
                raise ValueError(
                    "Server did not respond with user details, either API_KEY is invalid or server is down."
                )
        except Exception:
            self.log(
                "error",
                "Failed to fetch user details from API; attempting to load from local.",
                exc_info=True,
            )
            # Attempt to load from local file if server is down or data fetch failed
            self._load_user_details_from_local()

    def _save_user_details_locally(self, user_details: Dict[str, Any]) -> None:
        """
        Saves the user details to a local file.

        Args:
            user_details (dict): The user details to be saved.

        Returns:
            None
        """
        self.log("debug", "Saving user details locally.")
        data_dir = self._get_create_data_dir()
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            self.log("debug", f"Created data directory at {data_dir}.")
        file_path = os.path.join(data_dir, "user_details.json")
        try:
            with open(file_path, "w") as file:
                json.dump(user_details, file)
            self.log("info", "User details saved locally.")
        except Exception:
            self.log("error", "Failed to save user details locally.", exc_info=True)

    def _load_user_details_from_local(self) -> None:
        """
        Loads the user details from a local file.

        Returns:
            None
        """
        self.log("debug", "Loading user details from local file.")
        data_dir = self._get_create_data_dir()
        file_path = os.path.join(data_dir, "user_details.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as file:
                    user_details = json.load(file)
                    self.customer_id = user_details.get("id", None)
                    if not self.connection_details:
                        self.connection_details = user_details.get(
                            "connection_string", self.connection_details
                        )
                self.log("info", "User details loaded from local file successfully.")
            except Exception:
                self.log(
                    "error",
                    "Failed to load user details from local file.",
                    exc_info=True,
                )
        else:
            self.log("warning", f"Local user details file does not exist at {file_path}.")

    def _make_request(
        self, url: str, method: Optional[str] = "GET", body: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Union[Dict[str, Any], str], int]:
        """
        A method for making API calls.

        Args:
            url (str): The API endpoint URL.
            method (str, optional): The HTTP method. Defaults to "GET".
            body (dict, optional): The request body for POST/PUT requests.

        Returns:
            Tuple[str, Union[Dict, str], int]: A tuple containing status message, response data, and HTTP status code.
        """
        self.log("debug", f"Making {method.upper()} request to URL: {url} with body: {body}")
        headers = {"Authorization": f"Bearer {self.arched_api_key}"}

        try:
            method = method.lower()
            if method == "get":
                response = requests.get(url, headers=headers)
            elif method == "post":
                response = requests.post(url, json=body, headers=headers)
            elif method == "put":
                response = requests.put(url, json=body, headers=headers)
            elif method == "delete":
                response = requests.delete(url, headers=headers)
            else:
                self.log("error", f"Unsupported HTTP method: {method.upper()}")
                return "Error", "Unsupported method", 500

            self.log("debug", f"Received response with status code: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.log("debug", "Response JSON parsed successfully.")
                    return "Success:", data, 200
                except ValueError:
                    self.log("debug", "Response is not JSON; returning text.")
                    return "Success:", response.text, 200
            else:
                try:
                    error_data = response.json()
                    self.log(
                        "warning",
                        f"API request failed with status {response.status_code}: {error_data}",
                    )
                    return "Error:", error_data, response.status_code
                except ValueError:
                    self.log(
                        "warning",
                        f"API request failed with status {response.status_code}: {response.text}",
                    )
                    return "Error:", response.text, response.status_code
        except requests.RequestException as e:
            self.log("error", "HTTP request failed.", exc_info=True)
            return "Error", str(e), 500

    def _load_env(self) -> None:
        """
        Load environment variables from encoded connection details.

        This method decodes the given connection details, splits it into key-value pairs,
        and sets the corresponding environment variables.

        Returns:
            None
        """
        self.log("debug", "Loading environment variables from connection details.")
        if self.connection_details:
            try:
                decoded_bytes = base64.b64decode(self.connection_details)
                decoded_string = decoded_bytes.decode("utf-8")
                for val in decoded_string.split(";"):
                    if "=" in val:
                        key, value = val.split("=", 1)
                        os.environ[key] = value
                        self.log("debug", f"Set environment variable: {key}={value}")
                self.log("info", "Environment variables loaded successfully.")
            except Exception:
                self.log(
                    "error",
                    "Failed to load environment variables from connection details.",
                    exc_info=True,
                )
        else:
            self.log(
                "warning",
                "No connection details provided; skipping environment variable loading.",
            )

    def _get_create_data_dir(self) -> str:
        """
        Gets or creates a directory for storing data specific to the application.

        Returns:
            str: The path to the data directory.
        """
        try:
            import appdirs  # type: ignore

            app_data_dir = Path(appdirs.user_data_dir(self.app_name, self.app_author))
        except Exception:  # pragma: no cover - exercised when dependency missing
            # Fallback to temp directory if appdirs is unavailable
            app_data_dir = Path(os.path.join(tempfile.gettempdir(), f"{self.app_name}_data"))
        try:
            app_data_dir.mkdir(parents=True, exist_ok=True)
            self.log("debug", f"Data directory ensured at: {app_data_dir}")
        except Exception:
            self.log(
                "error",
                f"Failed to create data directory at {app_data_dir}.",
                exc_info=True,
            )
        return str(app_data_dir)

    def _get_email_path(self, typ: str = "error", task_id: Optional[int] = None) -> str:
        """
        Fetches the email template from the API and saves it to a local file.

        Args:
            typ (str, optional): Type of email ('error' or 'success'). Defaults to "error".
            task_id (int, optional): The task ID associated with the email.

        Returns:
            str: The path to the saved email template file.
        """
        self.log("debug", f"Fetching {typ} email template.")
        data_dir = self._get_create_data_dir()
        email_path = os.path.join(data_dir, f"{typ}.html")

        try:
            url = f"{BASE_URL}/email/{typ}"
            if task_id:
                url += f"?task={task_id}"
            resp_text = self._make_request(url)
            if resp_text[2] == 200:
                with open(email_path, "w") as f:
                    f.write(resp_text[1])
                self.log("info", f"{typ.capitalize()} email template saved at {email_path}.")
            else:
                self.log("error", f"Failed to fetch {typ} email template: {resp_text[1]}")
        except Exception:
            self.log(
                "error",
                f"Exception occurred while fetching {typ} email template.",
                exc_info=True,
            )

        return email_path

    def log_message(
        self, log_level: str, text: str, task_id: Optional[int] = None
    ) -> Tuple[str, Union[Dict[str, Any], str], int]:
        """
        Logs a message to the specified logging endpoint.

        Args:
            log_level (str): The level of the log (e.g., "INFO", "ERROR", "DEBUG").
            text (str): The log message to be sent.
            task_id (int, optional): The task ID associated with the log.

        Returns:
            Tuple[str, Union[Dict, str], int]: The response status, response data, and HTTP status code.
        """
        self.log("debug", f"Logging message with level {log_level}: {text}")
        task_id = task_id or self.task_id

        url = f"{BASE_URL}/logger/{task_id}"
        log_data = {"log_level": log_level, "text": text}

        response = self._make_request(url, method="POST", body=log_data)
        if response[2] == 200:
            self.log("info", f"Log message sent successfully: {text}")
        else:
            self.log("error", f"Failed to send log message: {response[1]}")
        # Normalize status text for callers/tests
        status_text = response[0]
        if isinstance(status_text, str) and status_text.startswith("Error"):
            status_text = "Error"
        return status_text, response[1], response[2]

    def send_email(
        self,
        sender_email: str,
        sender_name: str,
        recipients: Union[str, list],
        subject: str,
        cc_recipients: Optional[Union[str, list]] = None,
        bcc_recipients: Optional[Union[str, list]] = None,
        dkim_selector: Optional[str] = "default",
        template: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """
        Sends an email.

        Args:
            sender_email (str): The email address of the sender.
            sender_name (str): The name of the sender.
            recipients (Union[str, list]): The email address(es) of the recipient(s).
            subject (str): The subject of the email.
            cc_recipients (Union[str, list], optional): CC recipient(s).
            bcc_recipients (Union[str, list], optional): BCC recipient(s).
            dkim_selector (str, optional): DKIM selector. Defaults to "default".
            template (str, optional): The template for the email.
            **kwargs: Additional keyword arguments for the `send_email` method.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        self.log(
            "debug",
            f"Sending email from {sender_email} to {recipients} with subject '{subject}'.",
        )
        try:
            os.environ["MAIL_DKIM_SELECTOR"] = dkim_selector
            self.mailer = SmtpMailer(sender_email, sender_name)
            success = self.mailer.send_email(
                recipients,
                cc_recipients=cc_recipients,
                bcc_recipients=bcc_recipients,
                subject=subject,
                template=template,
                **kwargs,
            )
            if success:
                self.log("info", f"Email sent successfully to {recipients}.")
            else:
                self.log("warning", f"Email failed to send to {recipients}.")
            return success
        except Exception:
            self.log("error", "Exception occurred while sending email.", exc_info=True)
            return False

    def _allowed_to_send(self, exception: Union[str, Exception], allowed_minutes: int = 60) -> bool:
        """
        Checks if the exception is allowed to send based on the allowed_minutes.

        Args:
            exception (Union[str, Exception]): The exception or error message to be checked.
            allowed_minutes (int, optional): Minutes within which the exception is not allowed to resend. Defaults to 60.

        Returns:
            bool: True if allowed to send, False otherwise.
        """
        exception_text = str(exception)
        self.log("debug", f"Checking if allowed to send exception: {exception_text}")
        current_time = datetime.datetime.now()

        # Make the check-and-update atomic to avoid duplicate sends under concurrency
        with self._lock:
            last_sent = self.errors_name_time.get(exception_text)
            if last_sent:
                elapsed = (current_time - last_sent).total_seconds() / 60  # minutes
                self.log("debug", f"Elapsed time since last sent: {elapsed} minutes.")
                if elapsed < allowed_minutes:
                    self.log(
                        "info",
                        f"Exception '{exception_text}' sent {elapsed} minutes ago; skipping email.",
                    )
                    return False

            # Update the timestamp; save happens outside the lock to prevent deadlock
            self.errors_name_time[exception_text] = current_time

        # Persist the updated throttling map
        self._save_error_log()
        self.log(
            "debug",
            f"Allowed to send exception '{exception_text}'; updated last sent time.",
        )
        return True

    def _send_to_db(self, success: bool = True, **kwargs: Any) -> None:
        """
        Send the email attempt to the database.

        Args:
            success (bool, optional): Whether the email was sent successfully. Defaults to True.
            **kwargs (dict): The keyword arguments for the email attempt.

        Returns:
            None
        """
        self.log("debug", "Sending email attempt to the database.")
        if kwargs.get("task_id"):
            data = {
                "sent_to": kwargs.get("recipients"),
                "sent_from": kwargs.get("sender"),
                "success": success,
                "html_response": kwargs.get("html"),
                "task_id": kwargs.get("task_id"),
            }
            response = self._make_request(
                f"{BASE_URL}/email/tasks/taskrun", method="POST", body=data
            )
            if response[2] == 200:
                self.log("info", "Email attempt logged to the database successfully.")
            else:
                self.log(
                    "error",
                    f"Failed to log email attempt to the database: {response[1]}",
                )

    def _get_html_content(self, message: MIMEMultipart):
        """
        Get the HTML content of the email.

        Args:
            message (MIMEMultipart): The MIMEMultipart object.

        Returns:
            str: The HTML content of the email.
        """
        self.log("debug", "Extracting HTML content from email message.")
        html_content = ""
        for part in message.walk():
            # Check if the content type is HTML
            if part.get_content_type() == "text/html":
                # Get the HTML content and stop looping
                charset = part.get_content_charset() or "utf-8"
                html_content = part.get_payload(decode=True).decode(charset, errors="replace")
                self.log("debug", "HTML content extracted successfully.")
                break
        if not html_content:
            self.log("warning", "No HTML content found in the email message.")
        return html_content

    def send_success_email(
        self,
        recipients: Union[str, list],
        dump_time_taken: Optional[bool] = True,
        dkim_selector: str = "default",
        sender: Optional[str] = None,
        sender_name: Optional[str] = None,
        app: Optional[str] = None,
        task_id: Optional[int] = None,
        update_db_only: Optional[bool] = False,
        **kwargs: Any,
    ) -> None:
        """
        Sends a success email.

        Args:
            recipients (Union[str, list]): The recipients of the success email.
            dump_time_taken (bool, optional): Whether to include the time taken in the email. Defaults to True.
            dkim_selector (str, optional): DKIM selector. Defaults to "default".
            sender (str, optional): The email address of the sender.
            sender_name (str, optional): The name of the sender.
            app (str, optional): The name of the application.
            task_id (int, optional): The task ID associated with the email.
            update_db_only (bool, optional): Whether to only update the database without sending the email. Defaults to False.
            **kwargs: Additional keyword arguments for the `send_email` method.

        Returns:
            None
        """
        self.log("debug", "Preparing to send success email.")
        try:
            if sender:
                self.success_mailer = SmtpMailer(sender, sender_name)
                self.log("debug", f"Success mailer updated with sender: {sender}.")

            # gets and creates the email template
            email_path = self._get_email_path(
                typ="success", task_id=task_id if task_id else self.task_id
            )

            # sets the DKIM selector, needed for sending emails from the server
            os.environ["MAIL_DKIM_SELECTOR"] = dkim_selector
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

            time_taken = datetime.datetime.now() - self.time_start if self.time_start else None
            if dump_time_taken and self.time_start:
                # add the time taken to the kwargs
                kwargs["time_taken"] = str(time_taken).split(".")[0]
                # reset the time taken
                self._log_timer(True)
                self.log("debug", f"Time taken added to email: {kwargs['time_taken']}.")

            app_name = app if app else self.app
            if not update_db_only:
                self.success_mailer.send_email(
                    recipients,
                    subject=f"Success: {app_name} - {generate_random_string()}",
                    template=email_path,
                    date=date,
                    app=app_name,
                    **{k: (redact_text(v) if isinstance(v, str) else v) for k, v in kwargs.items()},
                )
                self.log("info", f"Success email sent to {recipients}.")

                html_content = None
                try:
                    if hasattr(self.success_mailer, "message"):
                        html_content = self._get_html_content(self.success_mailer.message)
                except Exception:
                    # If the message object isn't a real email, skip HTML extraction
                    html_content = None
            else:
                html_content = None
                self.log("debug", "Update DB only flag is set; skipping email sending.")

            self._send_to_db(
                success=True,
                recipients=recipients,
                sender=self.success_mailer.sender.email if self.success_mailer else sender,
                html=html_content,
                task_id=task_id if task_id else self.task_id,
                **{k: (redact_text(v) if isinstance(v, str) else v) for k, v in kwargs.items()},
            )
        except Exception:
            self.log(
                "error",
                "Exception occurred while sending success email.",
                exc_info=True,
            )

    def send_error_email(
        self,
        recipients: Union[str, list],
        error_text: Optional[str] = None,
        exception: Optional[Exception] = None,
        include_tb: bool = True,
        dump_enviro: bool = True,
        dump_globals: bool = True,
        dump_locals: bool = True,
        dkim_selector: str = "default",
        sender: Optional[str] = None,
        sender_name: Optional[str] = None,
        allowed_minutes: Optional[int] = 60,
        task_id: Optional[int] = None,
        app: Optional[str] = None,
        send_to_db: Optional[bool] = True,
    ) -> None:
        """
        Sends an error email.

        Args:
            recipients (Union[str, list]): The recipients of the error email.
            error_text (str, optional): The error message to be included in the email.
            exception (Exception, optional): The exception object associated with the error.
            include_tb (bool, optional): Whether to include the traceback in the email. Defaults to True.
            dump_enviro (bool, optional): Whether to include the environment variables in the email. Defaults to True.
            dump_globals (bool, optional): Whether to include the global variables in the email. Defaults to True.
            dump_locals (bool, optional): Whether to include the local variables in the email. Defaults to True.
            dkim_selector (str, optional): DKIM selector. Defaults to "default".
            sender (str, optional): The email address of the sender.
            sender_name (str, optional): The name of the sender.
            allowed_minutes (int, optional): Minutes within which the same exception won't trigger another email. Defaults to 60.
            task_id (int, optional): The task ID associated with the email.
            app (str, optional): The name of the application.
            send_to_db (bool, optional): Whether to send the email attempt to the database. Defaults to True.

        Returns:
            None
        """
        self.log("debug", "Preparing to send error email.")
        try:
            if sender:
                self.mailer = SmtpMailer(sender, sender_name)
                self.log("debug", f"Mailer updated with sender: {sender}.")

            # gets and creates the email template
            email_path = self._get_email_path(
                typ="error", task_id=task_id if task_id else self.task_id
            )

            # sets the DKIM selector, needed for sending emails from the server
            os.environ["MAIL_DKIM_SELECTOR"] = dkim_selector
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            error_id = generate_random_string()

            template_data = {}
            if include_tb:
                tb_text: str = ""
                try:
                    if (
                        exception is not None
                        and getattr(exception, "__traceback__", None) is not None
                    ):
                        tb_text = "".join(
                            traceback.format_exception(
                                type(exception), exception, exception.__traceback__
                            )
                        )
                    else:
                        # Fallback to current exception context (may be empty outside except blocks)
                        tb_text = traceback.format_exc()
                except Exception:
                    tb_text = ""
                template_data["traceback"] = redact_text(tb_text)
                if exception is not None:
                    template_data["exception_type"] = type(exception).__name__
                    template_data["exception_message"] = redact_text(str(exception))
                self.log("debug", "Traceback included in error email.")
            if dump_enviro:
                template_data["enviro"] = obfuscate_sensitive_info(dict(os.environ))
                self.log("debug", "Environment variables included in error email.")
            for dump_ok, dump_type, dump_ob in [
                [dump_globals, "globals", globals],
                [dump_locals, "locals", locals],
            ]:
                if dump_ok:
                    dump_dict = {}
                    for k in dump_ob().keys():
                        if k not in ["request", "session"]:
                            val = str(dump_ob().get(k))
                            dump_dict.update(obfuscate_sensitive_info({str(k): val}))
                    template_data[str(dump_type)] = dump_dict
                    self.log(
                        "debug",
                        f"{dump_type.capitalize()} variables included in error email.",
                    )

            # Prefer the exception message for throttling identity; fall back to provided text or formatted traceback
            issue = (
                (redact_text(str(exception)) if exception is not None else None)
                or (redact_text(error_text) if error_text else None)
                or (template_data.get("traceback") if include_tb else None)
                or "UnknownError"
            )
            if issue:
                if self._allowed_to_send(issue, allowed_minutes=allowed_minutes):
                    app_name = app if app else self.app
                    self.mailer.send_email(
                        recipients,
                        subject=f"Error: {app_name} - {error_id}",
                        template=email_path,
                        date=date,
                        app=app_name,
                        error_id=error_id,
                        exception=exception,
                        error_text=redact_text(error_text) if error_text else None,
                        **{
                            k: (redact_text(v) if isinstance(v, str) else v)
                            for k, v in template_data.items()
                        },
                    )
                    self.log("info", f"Error email sent to {recipients}.")

                    html = None
                    if hasattr(self.mailer, "message"):
                        try:
                            html = self._get_html_content(self.mailer.message)
                        except Exception:
                            html = None
                    if send_to_db:
                        self._send_to_db(
                            success=False,
                            recipients=recipients,
                            sender=self.mailer.sender.email if self.mailer else sender,
                            html=redact_text(html) if isinstance(html, str) else html,
                            task_id=task_id if task_id else self.task_id,
                            **{
                                k: (redact_text(v) if isinstance(v, str) else v)
                                for k, v in template_data.items()
                            },
                        )
                else:
                    self.log("info", "Error email not sent due to throttling.")
        except Exception:
            self.log("error", "Exception occurred while sending error email.", exc_info=True)
            # Ensure failures are still recorded in the backend when requested
            if send_to_db:
                try:
                    self._send_to_db(
                        success=False,
                        recipients=recipients,
                        sender=(
                            self.mailer.sender.email
                            if getattr(self, "mailer", None)
                            and getattr(self.mailer, "sender", None)
                            else sender
                        ),
                        html=None,
                        task_id=task_id if task_id else self.task_id,
                    )
                except Exception:
                    # Swallow any logging errors to avoid masking the original issue
                    pass

    def try_log_function(
        self,
        error_recipients: Union[str, list],
        send_success: Optional[bool] = False,
        success_recipients: Optional[Union[str, list]] = None,
        allowed_minutes: Optional[int] = 60,
        send_to_db: Optional[bool] = True,
        task_id: Optional[int] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        A decorator for logging the start time of a function and sending an error email if the function raises an
        exception. Optionally, it can also send a success email if the function completes successfully.

        Args:
            error_recipients (Union[str, list]): The recipients of the error email.
            send_success (bool, optional): Whether to send a success email if the function completes successfully. Defaults to False.
            success_recipients (Union[str, list], optional): The recipients of the success email.
            allowed_minutes (int, optional): Minutes within which the same exception won't trigger another email. Defaults to 60.
            send_to_db (bool, optional): Whether to send the email attempt to the database. Defaults to True.
            task_id (int, optional): The task ID associated with the email.
            *args: Additional positional arguments for the jinja email template.
            **kwargs: Additional keyword arguments for the jinja email template.

        Returns:
            function: The wrapped function.
        """
        self.log("debug", "Creating try_log_function decorator.")

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            def wrapper(*func_args: Any, **func_kwargs: Any) -> Any:
                self.log("debug", f"Function '{func.__name__}' started.")
                result = None

                self._log_timer()
                try:
                    result = func(*func_args, **func_kwargs)
                    self.log("debug", f"Function '{func.__name__}' executed successfully.")

                    success_text = (
                        "<strong style='font-size:larger'>Function Result: </strong>: <br> "
                    )
                    if result is not None:
                        if isinstance(result, dict):
                            success_text += (
                                json.dumps(result, indent=4)
                                .replace(" ", "&nbsp;")
                                .replace("\n", "<br>")
                            )
                        elif isinstance(result, (str, int, float)):
                            success_text += str(result)
                        else:
                            success_text += f"TYPE: {type(result)}"

                    if send_success and success_recipients:
                        self.send_success_email(
                            success_recipients,
                            success_text=success_text,
                            task_id=task_id,
                            **kwargs,
                        )
                        self.log("info", f"Success email sent to {success_recipients}.")
                    if not send_success and send_to_db:
                        self.send_success_email(
                            success_recipients,
                            success_text=success_text,
                            task_id=task_id,
                            update_db_only=True,
                            **kwargs,
                        )
                        self.log("debug", "Success email logged to database without sending.")
                except Exception as e:
                    self.log(
                        "error",
                        f"Exception in function '{func.__name__}': {e}",
                        exc_info=True,
                    )
                    self.send_error_email(
                        error_recipients,
                        exception=e,
                        allowed_minutes=allowed_minutes,
                        task_id=task_id,
                        **kwargs,
                    )
                finally:
                    self._log_timer(True)
                    self.log("debug", f"Function '{func.__name__}' finished.")
                    return result

            return wrapper

        return decorator

    def _log_timer(self, reset=False):
        """
        Log the start time of the application.

        Args:
            reset (bool, optional): Whether to reset the timer. Defaults to False.

        Returns:
            None
        """
        if reset:
            self.log("debug", "Resetting the timer.")
            self.time_start = None
            return
        self.time_start = datetime.datetime.now()
        self.log("debug", f"Timer started at {self.time_start}.")
