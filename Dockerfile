FROM python:3.8
LABEL maintainer="ayushi_gupta"

COPY techtrends /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python3", "init_db.py"]

EXPOSE 3111

CMD ["python3", "app.py"]