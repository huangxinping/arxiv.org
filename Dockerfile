FROM python:3.6.0-slim

RUN mkdir /src
COPY . /src

WORKDIR /src
RUN pip install --upgrade pip && pip install -r requirements.txt && find . -name "*.pyc" -delete

CMD ["python", "-u", "dingding.py"]
