FROM gcr.io/google-appengine/python
ADD . /app/
RUN chmod 777 ./ffmpeg
RUN pip install -r requirements.txt
CMD python conv.py globalhost