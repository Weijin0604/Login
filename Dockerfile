FROM python:3.10

# 安装 SQLite3
RUN apt-get update && apt-get install -y sqlite3

WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt

EXPOSE 3000

CMD python3 ./api.py