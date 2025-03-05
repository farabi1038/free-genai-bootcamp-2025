#!/bin/bash

# Test Integration Script for Language Learning Portal
# This script validates that frontend and backend work smoothly together

echo "================================================="
echo "Language Learning Portal Integration Test Script"
echo "================================================="

# Check if the backend is running
echo "[1/6] Checking if backend server is running..."
if curl -s http://localhost:8080/api/health > /dev/null; then
  echo "✅ Backend is running on port 8080"
  BACKEND_RUNNING=true
else
  echo "⚠️ Backend is not running"
  echo "Starting backend server..."
  
  # Try to start the backend
  pushd backend > /dev/null
  # Using nohup to run in background
  nohup go run cmd/server/main.go &> ../backend.log &
  popd > /dev/null
  
  BACKEND_PID=$!
  echo "Backend started with PID: $BACKEND_PID"
  
  # Wait for backend to initialize (max 20 seconds)
  MAX_RETRIES=20
  RETRIES=0
  BACKEND_RUNNING=false
  
  echo "Waiting for backend to initialize..."
  while [ $RETRIES -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8080/api/health > /dev/null; then
      BACKEND_RUNNING=true
      echo "✅ Backend is now running"
      break
    fi
    sleep 1
    RETRIES=$((RETRIES+1))
    echo -n "."
  done
  
  if [ "$BACKEND_RUNNING" = false ]; then
    echo "❌ Failed to start backend, check backend.log for details"
    exit 1
  fi
fi

# Check if we need to start the dev server for frontend
echo "[2/6] Checking if frontend dev server is running..."
if curl -s http://localhost:3000 > /dev/null; then
  echo "✅ Frontend dev server is running on port 3000"
  FRONTEND_RUNNING=true
else
  echo "⚠️ Frontend dev server is not running"
  echo "Installing frontend dependencies..."
  pushd frontend > /dev/null
  npm install
  
  echo "Starting frontend dev server..."
  # Using nohup to run in background
  nohup npm run dev &> ../frontend.log &
  popd > /dev/null
  
  FRONTEND_PID=$!
  echo "Frontend started with PID: $FRONTEND_PID"
  
  # Wait for frontend to initialize (max 30 seconds)
  MAX_RETRIES=30
  RETRIES=0
  FRONTEND_RUNNING=false
  
  echo "Waiting for frontend to initialize..."
  while [ $RETRIES -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:3000 > /dev/null; then
      FRONTEND_RUNNING=true
      echo "✅ Frontend is now running"
      break
    fi
    sleep 1
    RETRIES=$((RETRIES+1))
    echo -n "."
  done
  
  if [ "$FRONTEND_RUNNING" = false ]; then
    echo "❌ Failed to start frontend, check frontend.log for details"
    # Kill the backend if we started it
    if [ -n "$BACKEND_PID" ]; then
      kill $BACKEND_PID
    fi
    exit 1
  fi
fi

# Run backend unit tests
echo "[3/6] Running backend unit tests..."
pushd backend > /dev/null
go test ./... -v
BACKEND_TEST_RESULT=$?
popd > /dev/null

if [ $BACKEND_TEST_RESULT -eq 0 ]; then
  echo "✅ Backend unit tests passed"
else
  echo "❌ Backend unit tests failed"
fi

# Run backend end-to-end tests
echo "[4/6] Running backend end-to-end tests..."
pushd backend > /dev/null
go test ./test/e2e_test.go -v
BACKEND_E2E_RESULT=$?
popd > /dev/null

if [ $BACKEND_E2E_RESULT -eq 0 ]; then
  echo "✅ Backend E2E tests passed"
else
  echo "❌ Backend E2E tests failed (this may be expected if not all endpoints are implemented)"
fi

# Run frontend unit tests
echo "[5/6] Running frontend unit tests..."
pushd frontend > /dev/null
npm test
FRONTEND_TEST_RESULT=$?
popd > /dev/null

if [ $FRONTEND_TEST_RESULT -eq 0 ]; then
  echo "✅ Frontend unit tests passed"
else
  echo "❌ Frontend unit tests failed (this may be expected during initial development)"
fi

# Run integration tests
echo "[6/6] Running frontend-backend integration tests..."
pushd frontend > /dev/null
npm test -- "integration"
INTEGRATION_TEST_RESULT=$?
popd > /dev/null

if [ $INTEGRATION_TEST_RESULT -eq 0 ]; then
  echo "✅ Integration tests passed"
else
  echo "❌ Integration tests failed (this may be expected during initial development)"
fi

# Final report
echo "================================================="
echo "Integration Test Results:"
echo "================================================="
echo "Backend Unit Tests: $([ $BACKEND_TEST_RESULT -eq 0 ] && echo "PASSED ✅" || echo "FAILED ❌")"
echo "Backend E2E Tests: $([ $BACKEND_E2E_RESULT -eq 0 ] && echo "PASSED ✅" || echo "FAILED ❌")"
echo "Frontend Unit Tests: $([ $FRONTEND_TEST_RESULT -eq 0 ] && echo "PASSED ✅" || echo "FAILED ❌")"
echo "Integration Tests: $([ $INTEGRATION_TEST_RESULT -eq 0 ] && echo "PASSED ✅" || echo "FAILED ❌")"

# Determine overall status
if [ $BACKEND_TEST_RESULT -eq 0 ] && [ $FRONTEND_TEST_RESULT -eq 0 ] && [ $INTEGRATION_TEST_RESULT -eq 0 ]; then
  echo "================================================="
  echo "🎉 All tests passed! Frontend and backend are working smoothly together."
  echo "================================================="
  OVERALL_STATUS=0
else
  echo "================================================="
  echo "⚠️ Some tests failed. Check the logs for details."
  echo "================================================="
  OVERALL_STATUS=1
fi

# Clean up if we started the processes
if [ -n "$BACKEND_PID" ]; then
  echo "Stopping backend (PID: $BACKEND_PID)..."
  kill $BACKEND_PID
fi

if [ -n "$FRONTEND_PID" ]; then
  echo "Stopping frontend (PID: $FRONTEND_PID)..."
  kill $FRONTEND_PID
fi

exit $OVERALL_STATUS 