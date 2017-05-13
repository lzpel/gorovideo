FROM gcr.io/google-appengine/python

ADD . /app/
RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:jon-severinsson/ffmpeg
RUN apt-get update
RUN apt-get install ffmpeg -y

CMD gunicorn -b :$PORT main:app