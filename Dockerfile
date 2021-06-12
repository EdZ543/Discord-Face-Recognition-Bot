# FROM jhonatans01/python-dlib-opencv
# COPY . /app
FROM scratch
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]