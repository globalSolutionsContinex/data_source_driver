#!/bin/bash
git pull
cp ../config/data_source_driver.toml ./data_source_driver.toml
docker build -t data_source_driver .
docker kill data_source_driver
docker rm data_source_driver
docker run -d --name data_source_driver data_source_driver python3 main.py data_source_driver.toml
