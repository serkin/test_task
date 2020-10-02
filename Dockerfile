FROM python:3.6-slim
ADD app.py /code/app.py
ADD requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python3", "app.py"]

