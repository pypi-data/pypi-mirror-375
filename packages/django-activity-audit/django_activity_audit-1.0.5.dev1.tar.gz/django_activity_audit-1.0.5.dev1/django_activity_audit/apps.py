from django.apps import AppConfig
import logging
from .handlers import AuditLogHandler
from .formatters import APIFormatter, AuditFormatter, LoginFormatter
from django.conf import settings
from . import logger_levels

import queue


class AuditLoggingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_activity_audit"
    verbose_name = "Django Activity Audit"

    def ready(self):
        # Register custom log levels
        logger_levels.AUDIT
        logger_levels.API
        logger_levels.LOGIN

        # Initialize signals
        from . import signals  # noqa

        # Read user-defined settings with defaults
        audit_conf = getattr(settings, "AUDIT_LOGGING", {})
        max_bytes = audit_conf.get("MAX_BYTES", 10 * 1024 * 1024)
        backup_count = audit_conf.get("BACKUP_COUNT", 5)

        api_file = audit_conf.get("API_LOG_FILE", "audit_logs/api.log")
        audit_file = audit_conf.get("AUDIT_LOG_FILE", "audit_logs/audit.log")
        login_file = audit_conf.get("LOGIN_LOG_FILE", "audit_logs/login.log")

        # --- Shared queue ---
        self.log_queue = queue.Queue(-1)

        # --- Create file handlers using user inputs ---
        api_file_handler = AuditLogHandler(
            filename=api_file, maxBytes=max_bytes, backupCount=backup_count
        )
        api_file_handler.setFormatter(APIFormatter())

        audit_file_handler = AuditLogHandler(
            filename=audit_file, maxBytes=max_bytes, backupCount=backup_count
        )
        audit_file_handler.setFormatter(AuditFormatter())

        login_file_handler = AuditLogHandler(
            filename=login_file, maxBytes=max_bytes, backupCount=backup_count
        )
        login_file_handler.setFormatter(LoginFormatter())

        # --- Start QueueListener ---
        self.queue_listener = logging.handlers.QueueListener(
            self.log_queue, api_file_handler, audit_file_handler, login_file_handler
        )
        self.queue_listener.start()

        # --- Attach QueueHandler to loggers ---
        queue_handler = logging.handlers.QueueHandler(self.log_queue)
        logger_map = {
            "audit.request": logger_levels.API,
            "audit.crud": logger_levels.AUDIT,
            "audit.login": logger_levels.LOGIN,
        }
        for logger_name, level in logger_map.items():
            logger = logging.getLogger(logger_name)
            logger.addHandler(queue_handler)
            logger.setLevel(level)
