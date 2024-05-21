import websocket
from kafka import KafkaProducer, errors as kafka_errors
import os
import finnhub
import avro.io
import io
import avro.schema
import json
from dotenv import load_dotenv
import time
load_dotenv()

class FinnhubProducerStreaming:

    def __init__(self):
        # Load env
        self.FINHUB_API_PWD = os.getenv('FINHUB_API_PWD')
        self.KAFKA_BROKER = os.getenv('KAFKA_BROKER')
        self.TOPIC_NAME = os.getenv('TOPIC_NAME')
        self.schema_path = "./schema/avro_schema.avsc"
        self.avro_schema = self.load_avro_schema()

        self.producer = self.load_producer()

        print("FINHUB_API_PWD:", self.FINHUB_API_PWD)  # Debugging statement
        print("KAFKA_BROKER:", self.KAFKA_BROKER)      # Debugging statement
        print("TOPIC_NAME:", self.TOPIC_NAME)          # Debugging statement

        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            f"wss://ws.finnhub.io?token={self.FINHUB_API_PWD}",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    # Set the finnhub client connection
    def load_client(self):
        return finnhub.Client(api_key=self.FINHUB_API_PWD)

    # Setting up a Kafka connection
    def load_producer(self):
        try : 
            producer = KafkaProducer(bootstrap_servers=self.KAFKA_BROKER)
            return producer
        except kafka_errors.NoBrokersAvailable:
            print("No Kafka brokers available. Make sure Kafka is running and the broker address is correct.")
            return KafkaProducer(bootstrap_servers=self.KAFKA_BROKER)
        

    # Parse Avro schema
    def load_avro_schema(self):
        with open(self.schema_path, 'r') as schema_file:
            return avro.schema.parse(schema_file.read())

    # Encode message into avro format
    def avro_encode(self, data, schema):
        writer = avro.io.DatumWriter(schema)
        bytes_writer = io.BytesIO()
        encoder = avro.io.BinaryEncoder(bytes_writer)
        writer.write(data, encoder)
        return bytes_writer.getvalue()

    def on_message(self, ws, message):
        message = json.loads(message)
        avro_message = self.avro_encode(
            {
                'data': message['data'],
                'type': message['type']
            },
            self.avro_schema
        )
        self.producer.send(self.TOPIC_NAME, avro_message)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        """
        Stock ticker I want to analyze
        """
        time.sleep(5)
        ws.send('{"type":"subscribe","symbol":"AAPL"}')
        ws.send('{"type":"subscribe","symbol":"AMZN"}')
        ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
        ws.send('{"type":"subscribe","symbol":"IC MARKETS:1"}')

if __name__ == "__main__":
    FinnhubProducerStreaming()
