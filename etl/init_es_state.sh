#!/bin/bash

ES_STATE_FILE="/usr/src/app/es_state.json"

# Check if the file exists
if [ ! -f "$ES_STATE_FILE" ]; then
  # If the file does not exist, create an empty file
  echo "{}" > "$ES_STATE_FILE"
fi

# Execute the main command of your container
exec "$@"
