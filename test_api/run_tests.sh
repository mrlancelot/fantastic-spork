#!/bin/bash

# Run the test suite with timeout handling
echo "Starting API Test Suite..."
echo "=========================="

# Set timeout to 60 seconds for the entire test
timeout 60 python test_api/test_all_endpoints.py 2>&1

# Check exit status
if [ $? -eq 124 ]; then
    echo ""
    echo "Test suite timed out after 60 seconds"
    echo "Some endpoints may be taking too long to respond"
fi

# Display results if available
if [ -f "test_api/test_results.json" ]; then
    echo ""
    echo "Test Results Summary:"
    echo "===================="
    python -c "
import json
with open('test_api/test_results.json', 'r') as f:
    data = json.load(f)
    summary = data.get('summary', {})
    print(f'Total Tests: {summary.get(\"total\", 0)}')
    print(f'Successful: {summary.get(\"success\", 0)}')
    print(f'Failed: {summary.get(\"failed\", 0)}')
    print(f'Errors: {summary.get(\"errors\", 0)}')
    print(f'Success Rate: {summary.get(\"success_rate\", 0):.1f}%')
    "
fi