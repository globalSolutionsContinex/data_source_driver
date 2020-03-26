cd ..
echo "Building docker image..."
docker build -t mercadoni_scheduled_jobs .
echo "Done"
echo "(Re)starting docker container..."
docker stop scheduled_jobs
docker rm scheduled_jobs
docker run --name scheduled_jobs -d mercadoni_scheduled_jobs:latest python3 main.py config/production.toml
echo "Done"
