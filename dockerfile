FROM python:3.9

ADD main.py .

RUN pip install requests beautifulsoup4 datetime

CMD [ "python3", "./main.py" ]
