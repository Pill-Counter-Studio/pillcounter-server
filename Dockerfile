FROM python:3.11.7-slim
WORKDIR /app
COPY ./requirements.txt .
RUN apt-get update && \
    apt-get install -y python3-pip python3-dev && \
    cd /usr/local/bin && \
    pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY src .

# Change timezone
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata
RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata

EXPOSE 8888
CMD [ "python", "main.py"]