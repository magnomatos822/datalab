#!/bin/bash
mkdir -p ./config/spark/jars
cd ./config/spark/jars

# Download das bibliotecas para integração S3/MinIO

wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar
wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.397/aws-java-sdk-bundle-1.12.397.jar
