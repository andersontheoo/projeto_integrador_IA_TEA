"""
Arquivo de configuração principal do Django para o projeto 'monan'.
Este arquivo define todas as configurações de sistema, paths, apps,
banco de dados, internacionalização, arquivos estáticos e mídia,
autenticação e segurança.
"""

from pathlib import Path
import os

# ============================================================
# PATHS
# ============================================================
# BASE_DIR é a raiz do projeto (onde está manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Diretórios adicionais de arquivos estáticos (CSS, JS, imagens)
STATICFILES_DIRS = [BASE_DIR / 'static']


# ============================================================
# CONFIGURAÇÃO RÁPIDA DE DESENVOLVIMENTO
# ============================================================
SECRET_KEY = 'django-insecure-*!y$-piwm_@b=xs!2upl4oakb-ku6x*@f^m=r3$*4_js31t88@'
# Chave secreta do Django. Deve ser mantida em segredo na produção.

DEBUG = True
# Modo debug ligado apenas para desenvolvimento.
# Não deixar True em produção.

ALLOWED_HOSTS = []
# Hosts permitidos para acessar o projeto.


# ============================================================
# APPS INSTALADOS
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',           # Painel de administração
    'django.contrib.auth',            # Sistema de autenticação
    'django.contrib.contenttypes',    # Tipos de conteúdo do Django
    'django.contrib.sessions',        # Gerenciamento de sessões
    'django.contrib.messages',        # Sistema de mensagens
    'django.contrib.staticfiles',     # Arquivos estáticos
    'core',                           # App principal do projeto
]


# ============================================================
# MIDDLEWARE
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ============================================================
# URLS E TEMPLATES
# ============================================================
ROOT_URLCONF = 'monan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Diretório de templates do projeto
        'APP_DIRS': True,                  # Procura templates nos apps instalados
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'monan.wsgi.application'


# ============================================================
# BANCO DE DADOS
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Banco de dados SQLite para dev
        'NAME': BASE_DIR / 'db.sqlite3',        # Arquivo do banco
    }
}


# ============================================================
# VALIDAÇÃO DE SENHAS
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# ============================================================
# INTERNACIONALIZAÇÃO
# ============================================================
LANGUAGE_CODE = 'pt-br'                # Idioma padrão
TIME_ZONE = 'America/Sao_Paulo'       # Fuso horário
USE_I18N = True                        # Habilita traduções
USE_TZ = True                          # Habilita timezone-aware


# ============================================================
# ARQUIVOS ESTÁTICOS
# ============================================================
STATIC_URL = '/static/'                # URL base para arquivos estáticos


# ============================================================
# ARQUIVOS DE MÍDIA / UPLOADS
# ============================================================
MEDIA_URL = '/media/'                  # URL base para mídia
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Diretório físico de uploads

# Pasta específica para armazenar avatares
AVATARS_DIR = os.path.join(MEDIA_ROOT, 'avatars')
os.makedirs(AVATARS_DIR, exist_ok=True)  # Cria a pasta se não existir


# ============================================================
# CONFIGURAÇÃO DE LOGIN
# ============================================================
LOGIN_URL = 'login'                    # Página de login
LOGIN_REDIRECT_URL = 'dashboard'       # Redireciona após login
LOGOUT_REDIRECT_URL = 'login'          # Redireciona após logout


# ============================================================
# SESSÕES
# ============================================================
SESSION_COOKIE_AGE = 1209600           # 2 semanas em segundos
SESSION_SAVE_EVERY_REQUEST = True      # Atualiza expiração a cada requisição


# ============================================================
# CONFIGURAÇÕES DE SEGURANÇA (produção)
# ============================================================
CSRF_COOKIE_SECURE = False             # Deve ser True em produção com HTTPS
SESSION_COOKIE_SECURE = False          # Deve ser True em produção com HTTPS
SECURE_BROWSER_XSS_FILTER = True       # Protege contra XSS
SECURE_CONTENT_TYPE_NOSNIFF = True     # Evita detecção incorreta de MIME


# ============================================================
# CAMPO PADRÃO PARA MODELOS
# ============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },

    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "system.log"),
            "formatter": "verbose",
        },
    },

    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
        "monan": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
