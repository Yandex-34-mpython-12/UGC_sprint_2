FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /tests/functional

COPY entrypoint.sh .
COPY requirements.txt .

RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

COPY . /tests/functional
WORKDIR /tests/functional

RUN chmod a+x entrypoint.sh