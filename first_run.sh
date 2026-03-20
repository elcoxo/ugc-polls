echo "First start"

echo "Starting Docker containers..."
docker compose -f docker-compose.yml up -d

echo "Running database migrations..."
docker compose -f docker-compose.yml exec backend python manage.py migrate

echo "Creating admin user"
docker compose -f docker-compose.yml exec backend python manage.py first_start

echo "Docker ready!"
echo "Now you can go to http://127.0.0.1:8000/admin/ and login"
echo "Username: admin"
echo "Password: admin"
