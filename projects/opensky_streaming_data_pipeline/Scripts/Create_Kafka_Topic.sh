docker-compose exec kafka \
  kafka-topics \
    --create \
    --topic planes \
    --partitions 1 \
    --replication-factor 1 \
    --if-not-exists \
    --zookeeper zookeeper:32181