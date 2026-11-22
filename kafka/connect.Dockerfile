FROM confluentinc/cp-kafka-connect:7.7.1

USER root
RUN confluent-hub install --no-prompt debezium/debezium-connector-postgresql:2.5.4-3 \
    && confluent-hub install --no-prompt confluentinc/kafka-connect-s3:10.5.7
USER appuser
