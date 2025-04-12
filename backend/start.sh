#!/usr/bin/env bash

# Wait for MySQL to be ready
until python init_db.py; do
  echo "Waiting for MySQL..."
  sleep 2
done

# Start the Flask application
python app.py 