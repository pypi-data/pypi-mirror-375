#!/bin/bash
set -e

# Test sudo permissions first
echo "Testing sudo permissions..."
sudo -l | grep chown || echo "No chown permissions found in sudo -l"

# Fix ownership of cache directories if they exist
if [ -d "/cache/model" ]; then
    echo "Setting ownership for /cache/model"
    echo "Before: $(ls -ld /cache/model)"
    if sudo chown -R app:app /cache/model; then
        echo "chown command succeeded"
    else
        echo "chown command failed with exit code: $?"
    fi
    echo "After: $(ls -ld /cache/model)"
fi

if [ -d "/cache/org" ]; then
    echo "Setting ownership for /cache/org"
    echo "Before: $(ls -ld /cache/org)"
    if sudo chown -R app:app /cache/org; then
        echo "chown command succeeded"
    else
        echo "chown command failed with exit code: $?"
    fi
    echo "After: $(ls -ld /cache/org)"
fi

# Execute the original command
exec "$@"
