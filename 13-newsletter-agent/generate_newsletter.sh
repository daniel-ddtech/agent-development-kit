#!/bin/bash

# Change to the newsletter agent directory
cd "$(dirname "$0")"

# Run the newsletter generator
python rated_newsletter_test.py

# Create a status file to indicate completion
echo "completed" > generation_status.txt

# Return success
echo "Newsletter generation completed"
