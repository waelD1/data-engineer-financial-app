FROM python:3.10.9


# Set the working directory inside the container
WORKDIR /app

# Copy the Python script, requirements.txt, and the schema directory
COPY ./finnhub_streaming_producer.py /app/
COPY ./requirements.txt /app/
COPY ./schema /app/schema


RUN apt-get clean && \
    apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install -r ./requirements.txt

CMD ["python","finnhub_streaming_producer.py"]