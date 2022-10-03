#Deriving the latest base image
FROM python:3.10.7-slim-buster

LABEL Maintainer="riyad@riyadc.com"

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5050"]
