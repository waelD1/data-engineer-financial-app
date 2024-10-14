import os
import uuid
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, from_unixtime, expr, current_timestamp,from_unixtime, expr
from pyspark.sql.avro.functions import from_avro
from dotenv import load_dotenv
import logging
import time
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
KAFKA_BROKER = os.getenv('KAFKA_BROKER')
TOPIC_NAME = os.getenv('TOPIC_NAME')

# Load Avro schema
avro_schema_file = "/opt/bitnami/spark/scripts/schema/avro_schema.avsc"
with open(avro_schema_file, "r") as file:
    avro_schema = file.read()


# Log Spark session creation
logger.info("Creating Spark session")

# Initialize Spark session
spark = SparkSession.builder\
    .appName('Financial application') \
    .config("spark.cassandra.connection.host", "cassandra") \
    .config("spark.cassandra.connection.port", "9042") \
    .config("spark.cassandra.auth.username", "cassandra") \
    .config("spark.cassandra.auth.password", "cassandra") \
    .getOrCreate()

logger.info("Spark session created")

# Read from Kafka
spark_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", TOPIC_NAME) \
    .option("maxOffsetsPerTrigger", "1000") \
    .option("useDeprecatedOffsetFetching", "false") \
    .load()

logger.info("Kafka read stream setup complete")

# Process the Avro data
processed_df = spark_df \
    .withColumn("avroData", from_avro(col("value"), avro_schema)) \
    .select("avroData.*") \
    .select(explode("data").alias("col"), "type") \
    .select("col.*")

# Renaming the columns and create unique ids and readable timestamp
processed_df_2 = processed_df.withColumnRenamed("p", "stock_price") \
                            .withColumnRenamed("s", "stock_symbol") \
                            .withColumnRenamed("v", "trade_volume") \
                            .withColumnRenamed("t", 'unix_trade_timestamp')\
                            .withColumn("date_trade_timestamp", from_unixtime(expr("unix_trade_timestamp / 1000"))) \
                            .withColumn("unique_id", expr("uuid()")) \
                            .drop("c") 
                            # .withColumnRenamed("c", "trade_conditions") \

logger.info("Data processing complete")

# Writing data to console
query = processed_df_2.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

logger.info("Data writing to console started")


# Write the result to cassandra DB
cassandra_query = processed_df_2 \
    .writeStream \
    .foreachBatch(lambda batch_df, epoch_id: batch_df.write.format("org.apache.spark.sql.cassandra").mode("append").option("keyspace", "finnhub_db").option("table", "trading_data").save()) \
    .trigger(processingTime = "10 seconds") \
    .start()

logger.info("Data writing to Cassandra started")


cassandra_query.awaitTermination()
query.awaitTermination()
