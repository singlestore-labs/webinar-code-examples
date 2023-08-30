FROM python:3.10-slim@sha256:cc91315c3561d0b87d0525cb814d430cfbc70f10ca54577def184da80e87c1db

WORKDIR /usr/app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python", "app.py" ]