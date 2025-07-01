# Dockerfile
FROM python:3.8

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app


# CMD ["uvicorn", "main:app", "--ssl-keyfile", "./key.pem", "--ssl-certfile", "./cert.pem", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# CMD ["uvicorn", "main:app", "--ssl-keyfile", "./key.pem", "--ssl-certfile", "./cert.pem", "--host", "0.0.0.0", "--port", "8000", "--reload"]
