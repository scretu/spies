FROM python:3.8-alpine

ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app

COPY spies/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY spies/proxy* ./

CMD [ "python", "./proxy.py" ]
