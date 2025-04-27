#!/bin/bash

# Run pytest to execute the tests
pytest

# Check if the tests passed or failed
if [ $? -eq 0 ]; then
  echo "Tests passed!"
else
  echo "Tests failed!"
  exit 1
fi