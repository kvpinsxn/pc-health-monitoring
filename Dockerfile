FROM python:3.11.11-slim-bookworm

RUN useradd --create-home --shell /usr/sbin/nologin appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --no-compile -r requirements.txt
COPY --chown=appuser:appuser app ./app
USER appuser
EXPOSE 8080
CMD ["python", "app/main.py"]

