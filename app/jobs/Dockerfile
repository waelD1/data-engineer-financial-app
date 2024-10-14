FROM bitnami/spark:3.5.0

# Switch to root user to install packages
USER root

# Update package list and install curl
RUN apt-get update && apt-get install -y curl

# Install Python packages
RUN pip install avro-python3==1.10.2 kafka-python==2.0.2 pyspark==3.5.0 python-dotenv==1.0.0

# Switch back to the default non-root user
USER 1001
