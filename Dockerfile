FROM gcr.io/google-appengine/python

ADD . /app/
RUN pip install -r requirements.txt

RUN apt-get install software-properties-common
RUN apt-get update
RUN apt-get install ffmpeg

CMD gunicorn -b :$PORT main:app