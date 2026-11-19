
# Python als Grundlage verwenden
FROM python:3.12-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# Abhängigkeiten kopieren
COPY requirements.txt .

# Python-Bibliotheken installieren
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien kopieren
COPY . .

# Port für Streamlit
EXPOSE 8501

# Streamlit-Webseite starten
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
