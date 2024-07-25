FROM python:3.11.7-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY src .
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
EXPOSE 8888
CMD [ "python", "main.py"]