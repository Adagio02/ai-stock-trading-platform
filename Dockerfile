FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY pyproject.toml .
COPY src ./src
COPY app ./app
COPY Models ./Models
COPY Reports ./Reports

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -e .

EXPOSE 8501

CMD ["streamlit", "run", "app/app.py", "--server.address=0.0.0.0"]