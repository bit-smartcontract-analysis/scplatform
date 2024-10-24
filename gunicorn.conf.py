import multiprocessing

bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count()*2 + 1
threads = 10
accesslog = "/var/log/scplatform/gunicorn_access.log"
errorlogb = "/var/log/scplatform/gunicorn_error.log"
preload_app = True
daemon = True
