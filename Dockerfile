FROM python:3.10.7

COPY ./src /app/src
COPY ./requirements.txt /app
COPY ./imdb_topgrossing.sql /app

WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 8000

ENV FLASK_APP=./src/app.py

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]