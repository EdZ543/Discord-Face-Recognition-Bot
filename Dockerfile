FROM jhonatans01/python-dlib-opencv
RUN pip3 install -r requirements.txt
CMD ["python3", "main.py"]