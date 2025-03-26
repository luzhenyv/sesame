# Remove old Flask files
rm -rf app/
rm -rf requirements.txt
rm -rf config.py

# Create new directory structure
mkdir -p app/api/v1
mkdir -p app/core
mkdir -p app/db
mkdir -p app/models
mkdir -p app/schemas
mkdir -p app/services
mkdir -p app/utils 