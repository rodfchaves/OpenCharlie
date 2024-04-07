#!/bin/bash
#Make this file executable: chmod +x build_docker_image.sh
docker build -t docker-compose:v1.0 .
docker run -d \
  --name my-postgres-container \
  -e POSTGRES_DB=gmcharlie \
  -e POSTGRES_USER=postgres \ # change the value to your username
  -e POSTGRES_PASSWORD=postgres \ # change the value to your password
  -v $(pwd)/init.sql:/docker-entrypoint-initdb.d/init.sql \
  postgres
docker run -p 5000:5000 docker-compose:v1.0

