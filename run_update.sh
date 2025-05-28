#!/bin/bash

# Default value for running server
RUN_SERVER=false

# Parse command line arguments
while getopts "s" opt; do
  case $opt in
    s)
      RUN_SERVER=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# Install requirements if needed
if ! python -c "import django" &> /dev/null; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Load environment variables
echo "Loading environment variables..."
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Run migrations
echo "Running makemigrations..."
python manage.py makemigrations api

echo "Running migrate..."
python manage.py migrate

# Copy database from remote server
echo "Copying database from remote server..."
# Create temporary key file with proper format
echo "$SSH_KEY" | tr -d '\r' > /tmp/hkn-portal-key.pem
chmod 600 /tmp/hkn-portal-key.pem
scp -i "/tmp/hkn-portal-key.pem" ubuntu@52.9.199.73:./hkn-portal/db.sqlite3 .
rm /tmp/hkn-portal-key.pem

# Start the development server if flag is set
if [ "$RUN_SERVER" = true ]; then
    echo "Starting development server..."
    python manage.py runserver
fi 