FROM python:3.8
WORKDIR /
COPY . /
RUN pip install -r requirements.txt
CMD ["python", "transfermane2.py"]