#!/bin/bash

# Verify that STAGE is set
if [ -z "$STAGE" ]; then
  echo "Error: Environment variable STAGE is not set."
  echo "Please set it using: export STAGE=<stage>"
  exit 1
fi

# List of directories
directories=(
  "t_books"
  "t_environments"
  "t_favorites"
  "t_libraries"
  "t_notifications"
  "t_reservations"
  "t_users"
)

# Deploy each service with the specified stage
for dir in "${directories[@]}"; do
  echo "Deploying service in $dir for stage $STAGE..."
  cd "$dir" || { echo "Failed to enter directory $dir"; exit 1; }
  sls deploy --stage "$STAGE" || { echo "Failed to deploy service in $dir"; exit 1; }
  cd ..
done

echo "All services deployed successfully for stage $STAGE!"
