FROM python:3.9

WORKDIR /service

COPY requirements.txt /service/requirements.txt
COPY entrypoint.sh /service/entrypoint.sh

RUN pip install --no-cache-dir --upgrade -r /service/requirements.txt

COPY app /service/app

ENTRYPOINT ["/service/entrypoint.sh"]