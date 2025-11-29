# Airport-API

Api service for cinema management written on DRF

# Installing using GitHub and preparing
Execute these commands

```
git clone https://github.com/Olexii-Babii/Airport-API.git
cd Airport-Api
python -m venv venv
source venv/bin/activate
pip install -r requrements.txt
echo "POSTGRES_PASSWORD=<your password>" > .env
echo "POSTGRES_USER=<your user>" >> .env
echo "POSTGRES_DB=<your db>" >> .env
echo "POSTGRES_HOST=<your host>" >> .env
echo "POSTGRES_PORT=<your port>" >> .env
echo "PGDATA=<your route>" >> .env
```
# Run with docker
Docker should be installed
```
docker compose build
docker compose up
```

# Getting access

- create user via /api/user/register/
- get access token via /api/user/token/

# Features
- JWT authenticated
- Admin panel /admin/
- Documentation is located at /api/doc/swagger/
- Managing orders and tickets
- Creating airplane with airplane_type
- Creating route with airports
- Creating flight with route and airplane
- Creating crew with flights
- Adding flights
- Filtering flights by source, destination, departure and arrival time
