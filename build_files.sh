#!/bin/bash

# Build the project
echo "Building the project..."

# Install dependencies
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Make migrations
echo "Making migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Build completed!"
