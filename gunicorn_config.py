bind = "0.0.0.0:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# SSL Configuration (if using HTTPS directly through Gunicorn)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
