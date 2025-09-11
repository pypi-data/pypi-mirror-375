#!/bin/bash
set -e

# Fix ownership of cache directories if they exist
if [ -d "/cache/model" ]; then
    echo "Setting ownership for /cache/model"
    sudo chown -R app:app /cache/model
fi

if [ -d "/cache/org" ]; then
    echo "Setting ownership for /cache/org"  
    sudo chown -R app:app /cache/org
fi

# Execute the original command
exec "$@"
