sudo systemctl restart docker # Avoid Error / "Docker compose error while creating mount source path"

docker container stop app
docker container stop worker
docker container stop nginx
docker container stop redis

docker container rm app
docker container rm worker
docker container rm nginx
docker container rm redis

sudo docker-compose build
sudo docker-compose up &

#sudo docker-compose up -d
docker-compose ps 


