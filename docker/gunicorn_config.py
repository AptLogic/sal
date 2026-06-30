import multiprocessing
from os import getenv
bind = '127.0.0.1:8001'

workers = multiprocessing.cpu_count() * 2 + 1
graceful_timeout = 45
timeout = 60
# Keep-alive connections reduce overhead of creating new connections
keepalive = 5

pidfile = '/var/run/gunicorn.pid'

errorlog = '/var/log/gunicorn/gunicorn-error.log'
loglevel = 'critical'

# Read the DEBUG setting from env var
try:
    if getenv('DOCKER_SAL_DEBUG').lower() == 'true':
        accesslog = '/var/log/gunicorn/gunicorn-access.log'
        loglevel = 'info'
except Exception:
    pass

# Protect against memory leaks by restarting each worker every 1000
# requests, with a randomized jitter of 0-50 requests to avoid thunderding herd
max_requests = 1000
max_requests_jitter = 50
worker_class = 'gevent'
# Improve connection handling for gevent with increased backlog
backlog = 2048


# Patch psycopg to better work with gevent greenlets
def post_fork(server, worker):
    from psycogreen.gevent import patch_psycopg
    patch_psycopg()
