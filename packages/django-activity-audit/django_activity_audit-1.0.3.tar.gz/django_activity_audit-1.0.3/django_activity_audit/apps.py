from django.apps import AppConfig
import logging
from .handlers import AuditLogHandler


class AuditLoggingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_activity_audit"
    verbose_name = "Django Activity Audit"

    def ready(self):
        # Import and register custom log levels
        from . import logger_levels

        # Force registration of custom levels
        logger_levels.AUDIT
        logger_levels.API
        logger_levels.LOGIN

        # Initialize signals
        from . import signals  # noqa

        # --- Shared queue for async logging ---
        self.log_queue = logging.handlers.Queue(-1)

        api_file_handler = AuditLogHandler(filename="audit_logs/api.log")
        audit_file_handler = AuditLogHandler(filename="audit_logs/audit.log")
        login_file_handler = AuditLogHandler(filename="audit_logs/login.log")

        # --- Start QueueListener for async writing ---
        self.queue_listener = logging.handlers.QueueListener(
            self.log_queue,
            api_file_handler,
            audit_file_handler,
            login_file_handler,
        )
        self.queue_listener.start()

        # --- Attach QueueHandler to loggers ---

        logger_map = {
            "audit.request": logger_levels.API,
            "audit.crud": logger_levels.AUDIT,
            "audit.login": logger_levels.LOGIN,
        }

        queue_handler = logging.handlers.QueueHandler(self.log_queue)

        for logger_name, level in logger_map.items():
            logger = logging.getLogger(logger_name)
            logger.addHandler(queue_handler)
            logger.setLevel(level)
