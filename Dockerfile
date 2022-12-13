# syntax=docker/dockerfile:1

FROM arm64v8/python:3.8-slim-buster
RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
COPY run.py run.py
COPY pyqvrpro pyqvrpro
RUN mkdir -p recording

RUN pip install -r requirements.txt

ENV FLASK_APP=run.py
ENV FLASK_RUN_PORT=5000
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["python", "-m", "flask", "run"]