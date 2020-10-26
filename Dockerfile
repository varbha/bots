FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get install git


COPY . .
RUN chmod -R 777 /usr/src/app

CMD [ "python", "./_botMain.py" ]
