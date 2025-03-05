#!/bin/bash

# Change to the project root directory
cd "$(dirname "$0")/.." || exit

# Run the tests with verbose output and coverage report
go test -v ./test -coverprofile=coverage.out

# Display the coverage report
go tool cover -func=coverage.out

echo ""
echo "To view the coverage report in HTML format, run:"
echo "go tool cover -html=coverage.out" 