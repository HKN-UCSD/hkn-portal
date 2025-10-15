#!/bin/bash

# Default values
VENV_NAME="venv" ## ASSUMES VENV IS IN THE SAME DIRECTORY AS THIS SCRIPT
RUN_SETUP=false

# Parse command line arguments
while getopts "sv:" opt; do
  case $opt in
    s)
      RUN_SETUP=true
      ;;
    v)
      VENV_NAME="$OPTARG"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# Activate virtual environment
echo "Activating virtual environment: $VENV_NAME"
if [ -d "$VENV_NAME" ]; then
    if source "$VENV_NAME/Scripts/activate" 2>/dev/null; then
        echo "Activated virtual environment via Scripts/activate"
    elif source "$VENV_NAME/bin/activate" 2>/dev/null; then
        echo "Activated virtual environment via bin/activate"
    else
        echo "Error: Could not activate virtual environment (no valid activate script found)." >&2
        exit 1
    fi
else
    echo "Virtual environment '$VENV_NAME' not found!"
    exit 1
fi

if [ "$RUN_SETUP" = true ]; then
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

    # Setup frontend
    echo "Setting up frontend..."
    cd frontend
    npm install
    cd ..
fi

# Start both servers
echo "Starting servers..."

# Start Django server in the background
echo "Starting Django server..."
python manage.py runserver &
DJANGO_PID=$!

# Start frontend server
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Function to handle script termination
cleanup() {
    echo "Shutting down servers..."
    kill $DJANGO_PID
    kill $FRONTEND_PID
    exit
}

# Set up trap to catch termination signal
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait $DJANGO_PID $FRONTEND_PID 