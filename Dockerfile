FROM python:3.7

COPY . /opt/site

WORKDIR /opt/site

RUN apt-get install libopenjp2-7-dev
RUN python3 -m pip install -r requirements.txt

WORKDIR /opt/site/website

CMD ["python3", "site.py"]