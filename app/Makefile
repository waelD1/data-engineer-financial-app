	
spark-jobs:
		docker exec -ti spark-master /bin/bash -c "spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-avro_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0  scripts/spark_streaming.py"

CASSANDRA_CONTAINER=cassandra
CQL_SCRIPT_PATH=./cassandra/cassandra-init.cql

.PHONY: init-cassandra

init-cassandra:
	@echo "Copying CQL script to Cassandra container..."
	docker cp $(CQL_SCRIPT_PATH) $(CASSANDRA_CONTAINER):/cassandra-init.cql
	@echo "Executing CQL script in Cassandra container..."
	docker exec -it $(CASSANDRA_CONTAINER) cqlsh -u cassandra -p cassandra -f /cassandra-init.cql
	@echo "Cassandra keyspace and tables created."
