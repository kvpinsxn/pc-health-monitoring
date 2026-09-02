FROM python:3.11.11-slim-bookworm

RUN apt-get update \
	&& apt-get upgrade -y \
	&& rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /usr/sbin/nologin appuser
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade \
		"setuptools>=78.1.1,<81" \
		"wheel>=0.46.2,<1" \
	&& python -m pip install --no-cache-dir --no-compile -r requirements.txt
COPY --chown=appuser:appuser app ./app
USER appuser
EXPOSE 8080
CMD ["python", "app/main.py"]

