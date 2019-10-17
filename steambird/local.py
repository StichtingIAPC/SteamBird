
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': [
                'console'
            ],
            'level': 'WARNING',
            'propagate': True,
        },
        'steambird': {
            'handlers': [
                'console'
            ],
            'level': 'DEBUG',
            'propagate': True
        }
    },
}
