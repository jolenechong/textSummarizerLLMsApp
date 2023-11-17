# syntax=docker/dockerfile:1

# using debian slim version of python 3.11
FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt

# save space with torch downloads since we're not using GPU for inference
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip3 install peft flask Flask-SQLAlchemy transformers gevent psycopg2-binary python-dotenv langchain tiktoken boto3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/

COPY app.py .

# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"] # runs in development mode
CMD [ "python3", "-m", "app" ]