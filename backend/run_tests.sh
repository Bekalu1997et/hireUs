#!/bin/bash

# Script to run tests for the Structured Interview Platform

echo "=========================================="
echo "Running Tests for Authentication Module"
echo "=========================================="
echo ""

# Set PYTHONPATH to include the backend directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run database tests
echo "1. Running database session tests..."
pytest app/tests/test_database.py -v -m unit

echo ""
echo "2. Running security tests..."
pytest app/tests/test_security.py -v

echo ""
echo "3. Running authentication tests..."
pytest app/tests/test_auth.py -v

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
pytest app/tests/ -v --tb=short

echo ""
echo "Done!"
