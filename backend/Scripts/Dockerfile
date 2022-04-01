FROM python:3.9.10-alpine3.14

COPY . /home/

RUN pip install psycopg2-binary

RUN crontab /home/crontab

CMD ["crond", "-f"]