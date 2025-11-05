# Django settings for sal project.
from sal.system_settings import *
from sal.settings_import import *
from os import path


DATABASES = {
    "default": {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        "ENGINE": "django.db.backends.sqlite3",
        # Or path to database file if using sqlite3.
        "NAME": os.path.join(PROJECT_DIR, "db/sal.db"),
        "USER": "",  # Not used with sqlite3.
        "PASSWORD": "",  # Not used with sqlite3.
        "HOST": "",  # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",  # Set to empty string for default. Not used with sqlite3.
    }
}

# Memcached
if "MEMCACHED_PORT_11211_TCP_ADDR" in os.environ:
    addr = os.environ["MEMCACHED_PORT_11211_TCP_ADDR"]
    port = os.environ["MEMCACHED_PORT_11211_TCP_PORT"]
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": [f"{addr}:{port}", "11211"],
        }
    }

# PG Database
host = None
port = None

if "DB_USER" in os.environ:
    if "DB_HOST" in os.environ:
        host = os.environ.get("DB_HOST")
        port = os.environ.get("DB_PORT", "5432")

    elif "DB_PORT_5432_TCP_ADDR" in os.environ:
        host = os.environ.get("DB_PORT_5432_TCP_ADDR")
        port = os.environ.get("DB_PORT_5432_TCP_PORT", "5432")

    else:
        host = "db"
        port = "5432"

if host and port:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.environ["DB_PASS"],
            "HOST": host,
            "PORT": port,
        }
    }

if "AWS_IAM" in os.environ:
    import requests

    cert_bundle_url = (
        "https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem"
    )
    cert_target_path = "/etc/ssl/certs/global-bundle.pem"

    response = requests.get(cert_bundle_url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(cert_target_path), exist_ok=True)

        with open(cert_target_path, "wb") as file:
            file.write(response.content)
        print(
            f"AWS RDS cert bundle successfully downloaded and saved to {cert_target_path}"
        )
    else:
        print(
            f"Failed to download AWS RDS cert bundle, status code: {response.status_code}"
        )
    DATABASES = {
        "default": {
            "ENGINE": "django_iam_dbauth.aws.postgresql",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "HOST": os.environ["DB_HOST"],
            "PORT": os.environ["DB_PORT"],
            "OPTIONS": {
                "region_name": os.environ["AWS_RDS_REGION"],
                "sslmode": "verify-full",
                "sslrootcert": "/etc/ssl/certs/global-bundle.pem",
                "use_iam_auth": True,
            },
        }
    }

ADD_TO_ALL_BUSINESS_UNITS = os.environ.get("ADD_TO_ALL_BUSINESS_UNITS", "False")

if USE_SAML:
    import saml2
    from saml2.saml import NAMEID_FORMAT_PERSISTENT

    SAML_DJANGO_USER_MAIN_ATTRIBUTE = os.environ.get("SAML_USER_MAIN_ATTR", "email")
    SAML_USE_NAME_ID_AS_USERNAME = os.environ.get("SAML_NAME_ID_AS_USERNAME", True)
    SAML_CREATE_UNKNOWN_USER = os.environ.get("SAML_CREATE_UNKNOWN_USER", True)
    SAML_ATTR_NAME_UID = os.environ.get("SAML_ATTR_NAME_UID", "uid")
    SAML_ATTR_NAME_MAIL = os.environ.get("SAML_ATTR_NAME_MAIL", "mail")
    SAML_ATTR_NAME_CN = os.environ.get("SAML_ATTR_NAME_CN", "cn")
    SAML_ATTR_NAME_SN = os.environ.get("SAML_ATTR_NAME_SN", "sn")
    SAML_ATTRIBUTE_MAPPING = {
        SAML_ATTR_NAME_UID: (os.environ.get("SAML_ATTR_MAP_UID", "username"),),
        SAML_ATTR_NAME_MAIL: (os.environ.get("SAML_ATTR_MAP_MAIL", "email"),),
        SAML_ATTR_NAME_CN: (os.environ.get("SAML_ATTR_MAP_CN", "first_name"),),
        SAML_ATTR_NAME_SN: (os.environ.get("SAML_ATTR_MAP_SN", "last_name"),),
    }

    logging_config = get_sal_logging_config()
    if DEBUG:
        level = "DEBUG"
    else:
        level = "ERROR"
    logging_config["loggers"]["djangosaml2"] = {
        "propagate": False,
        "handlers": ["console"],
        "level": level,
    }
    update_sal_logging_config(logging_config)

    INSTALLED_APPS += ("djangosaml2",)
    MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "djangosaml2.middleware.SamlSessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "server.middleware.AddToBU.AddToBU",
    "search.current_user.CurrentUserMiddleware",
    )
    AUTHENTICATION_BACKENDS = (
        "django.contrib.auth.backends.ModelBackend",
        "djangosaml2.backends.Saml2Backend",
    )

    LOGIN_URL = os.environ.get("SAML_LOGIN_URL", "/saml2/login/")
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True

    # Pull SAML configs from environment variables (if they exist)
    SAML_CFG_ENTITYID = os.environ.get("SAML_CFG_ENTITYID","https://sal.example.com/saml2/metadata/")
    SAML_CFG_ALLOW_UNKNOWN_ATTRS = os.environ.get("SAML_CFG_ALLOW_UNKNOWN_ATTRS", True)
    SAML_SP_ACS_URL = os.environ.get("SAML_SP_ACS_URL","https://sal.example.com/saml2/acs/")
    SAML_SP_SLS_REDIR_URL = os.environ.get("SAML_SP_SLS_REDIR_URL","https://sal.example.com/saml2/ls/")
    SAML_SP_SLS_POST_URL = os.environ.get("SAML_SP_SLS_POST_URL","https://sal.example.com/saml2/ls/post")   
    SAML_IDP_ID_URL = os.environ.get("SAML_IDP_ID_URL","https://YOURID")
    SAML_IDP_SSO_URL = os.environ.get("SAML_IDP_SSO_URL","https://YOURSSOURL")
    SAML_IDP_SLS_URL = os.environ.get("SAML_IDP_SLS_URL","https://YOURSLOURL")
    SAML_IDP_META_URL = os.environ.get("SAML_METADATA_URL")

    BASEDIR = path.dirname(path.abspath(__file__))
    SAML_CONFIG = {
        # full path to the xmlsec1 binary programm
        "xmlsec_binary": "/usr/bin/xmlsec1",
        # your entity id, usually your subdomain plus the url to the metadata view
        "entityid": SAML_CFG_ENTITYID,
        # directory with attribute mapping
        "attribute_map_dir": path.join(BASEDIR, "attributemaps"),
        # this block states what services we provide
        "allow_unknown_attributes": SAML_CFG_ALLOW_UNKNOWN_ATTRS,
        "service": {
            # we are just a lonely SP
            "sp": {
                "authn_requests_signed": False,
                "allow_unsolicited": True,
                "want_assertions_signed": True,
                "want_response_signed": False,
                "allow_unknown_attributes": True,
                "name": "Sal",
                "name_id_format": NAMEID_FORMAT_PERSISTENT,
                "endpoints": {
                    # url and binding to the assetion consumer service view
                    # do not change the binding or service name
                    "assertion_consumer_service": [
                        (SAML_SP_ACS_URL, saml2.BINDING_HTTP_POST),
                    ],
                    # url and binding to the single logout service view
                    # do not change the binding or service name
                    "single_logout_service": [
                        (
                            SAML_SP_SLS_REDIR_URL,
                            saml2.BINDING_HTTP_REDIRECT,
                        ),
                        (
                            SAML_SP_SLS_POST_URL,
                            saml2.BINDING_HTTP_POST,
                        ),
                    ],
                },
                # attributes that this project need to identify a user
                "required_attributes": ["uid"],
                # attributes that may be useful to have but not required
                # 'optional_attributes': ['eduPersonAffiliation'],
                # in this section the list of IdPs we talk to are defined
                "idp": {
                    # we do not need a WAYF service since there is
                    # only an IdP defined here. This IdP should be
                    # present in our metadata
                    # the keys of this dictionary are entity ids
                    SAML_IDP_ID_URL: {
                        "single_sign_on_service": {
                            saml2.BINDING_HTTP_REDIRECT: SAML_IDP_SSO_URL,
                        },
                        "single_logout_service": {
                            saml2.BINDING_HTTP_REDIRECT: SAML_IDP_SLS_URL,
                        },
                    },
                },
            },
        },
        # where the remote metadata is stored
        "metadata": {
            "remote": [
                {
                    "url": SAML_IDP_META_URL
                },
            ],
        },
        # set to 1 to output debugging information
        "debug": 1,
        # certificate
        # 'key_file': path.join(BASEDIR, 'mycert.key'),  # private part
        
        #'cert_file': path.join(BASEDIR, 'cert.pem'),  # public part
        # own metadata settings
        # 'contact_person': [
        #     {'given_name': 'Lorenzo',
        #      'sur_name': 'Gil',
        #      'company': 'Yaco Sistemas',
        #      'email_address': 'lgs@yaco.es',
        #      'contact_type': 'technical'},
        #     {'given_name': 'Angel',
        #      'sur_name': 'Fernandez',
        #      'company': 'Yaco Sistemas',
        #      'email_address': 'angel@yaco.es',
        #      'contact_type': 'administrative'},
        #     ],
        # you can set multilanguage information here
        # 'organization': {
        #     'name': [('Someone', 'en'),
        #     'display_name': [('Someone', 'en')],
        #     'url': [('http://www.someone.com', 'en')],
        #     },
        "valid_for": 24,  # how long is our metadata valid
    }
