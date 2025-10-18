#!/bin/sh

# Wait for PostgreSQL before starting Django
echo "Waiting for PostgreSQL to be ready..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done

echo "Database is ready! Starting Django server..."
exec "$@"
