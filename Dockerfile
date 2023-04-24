FROM python3.10
WORKDIR /
COPY . /
RUN pip install -r requirements.txt
CMD ["python", "transfermane2.py"]