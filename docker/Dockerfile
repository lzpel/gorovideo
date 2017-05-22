FROM gcr.io/google-appengine/python
RUN pwd
ADD . /app/
RUN pwd
RUN ls
RUN chmod 777 /app/docker/ffmpeg
RUN pip install -r requirements.txt
CMD python conv.py globalhost