FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update
RUN apt-get install git


COPY . .

CMD [ "python", "./_botMain.py" ]
