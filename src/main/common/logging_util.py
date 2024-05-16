default_logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s %(name)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"]
    },
    "loggers": {
        "src": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False
        },
        "werkzeug": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False
        }
    }
}
