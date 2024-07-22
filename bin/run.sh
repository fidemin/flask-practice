
access_logfile="access.log"
error_logfile="error.log"
gunicorn -w 4 'src.main:create_app()' --bind 127.0.0.1:8000 \
  --access-logfile $access_logfile --error-logfile $error_logfile \
  --log-level info