from django.apps import AppConfig
import logging
import queue
from .handlers import AuditLogHandler
from .formatters import APIFormatter, AuditFormatter, LoginFormatter
from . import logger_levels


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

        # Shared in-memory queue
        self.log_queue = queue.Queue(-1)

        # Create actual file handlers (rotation optional)
        api_handler = AuditLogHandler(
            filename="audit_logs/api.log", maxBytes=10 * 1024 * 1024, backupCount=5
        )
        api_handler.setFormatter(APIFormatter())

        audit_handler = AuditLogHandler(
            filename="audit_logs/audit.log", maxBytes=10 * 1024 * 1024, backupCount=5
        )
        audit_handler.setFormatter(AuditFormatter())

        login_handler = AuditLogHandler(
            filename="audit_logs/login.log", maxBytes=10 * 1024 * 1024, backupCount=5
        )
        login_handler.setFormatter(LoginFormatter())

        # Start QueueListener
        self.queue_listener = logging.handlers.QueueListener(
            self.log_queue, api_handler, audit_handler, login_handler
        )
        self.queue_listener.start()

        # Attach QueueHandler to audit loggers
        queue_handler = logging.handlers.QueueHandler(self.log_queue)
        logger_map = {
            "audit.request": logger_levels.API,
            "audit.crud": logger_levels.AUDIT,
            "audit.login": logger_levels.LOGIN,
        }
        for name, level in logger_map.items():
            logger = logging.getLogger(name)
            logger.addHandler(queue_handler)
            logger.setLevel(level)
