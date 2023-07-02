FROM python:3.10 
WORKDIR /app 
COPY . /app
RUN apt-get update && apt-get install -y build-essential
RUN pip3 install -r requirements.txt 
EXPOSE 3000
CMD python3 ./api.py 

