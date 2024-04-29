FROM python:3.10

# Set working directory
WORKDIR /app

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3 python3-pip

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY /src .
COPY /test .

CMD ["python3"]

