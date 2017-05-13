FROM gcr.io/google-appengine/python

ADD . /app/
RUN pip install -r requirements.txt

RUN apt-get install software-properties-common
RUN add-apt-repository ppa:mc3man/trusty-media
RUN apt-get update
RUN apt-get install ffmpeg

CMD gunicorn -b :$PORT main:app