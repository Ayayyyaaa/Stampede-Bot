FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# On lance le bot
CMD ["python", "main.py"]