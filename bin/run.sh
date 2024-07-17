
gunicorn -w 4 'src.main:create_app()' --bind 127.0.0.1:8000