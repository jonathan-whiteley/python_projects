# Start Flask
docker-compose exec mids \
  env FLASK_APP=/W205_Project_3/OpenSkyFlask.py \
  flask run --host 0.0.0.0
