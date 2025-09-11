import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RECAPTCHA_PUBLIC_KEY = "6Lf_9MMrAAAAAOAsVXk8F5scxr6vsZJzC2jJnGHb"
RECAPTCHA_PRIVATE_KEY = "6Lf_9MMrAAAAAJqd_uA1_ekq3F-bD24KRhBcfKCF"

WAGTAIL_404_TEMPLATE = '404.html'

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "enap_designsystem.context_processors.navbar_context",
                "enap_designsystem.context_processors.recaptcha_context",
            ],
        },
    },
]



# AUMENTAR LIMITES DE UPLOAD E CAMPOS
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # Padrão é 1000
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB (padrão é 2.5MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB

# OUTRAS CONFIGURAÇÕES ÚTEIS PARA FORMULÁRIOS GRANDES
DATA_UPLOAD_MAX_NUMBER_FILES = 100  # Limite de arquivos por upload

# CONFIGURAÇÕES DE SEGURANÇA (se necessário)
SECURE_CROSS_ORIGIN_OPENER_POLICY = None  # Para evitar problemas com CORS