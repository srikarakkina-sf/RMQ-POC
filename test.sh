#!/bin/bash
# This script sends 1000 random curl requests to test the performance of the FastAPI app.

# Define the available endpoints.
endpoints=("add" "multiply" "subtract")

# Loop from 1 to 1000
for i in {1..1000}; do
  # Pick a random endpoint from the array
  ep=${endpoints[$((RANDOM % 3))]}
  # Generate two random numbers between 0 and 99 for x and y.
  x=$((RANDOM % 100))
  y=$((RANDOM % 100))
  
  # Build the URL (assuming your app is running on localhost:8000)
  url="http://localhost:8000/$ep?x=$x&y=$y"
  
  # Optionally print the URL to see the requests being made.
  echo "Request $i: $url"
  
  # Send the curl request in the background.
  curl -s "$url" > /dev/null &
done

# Wait for all background requests to complete.
wait
echo "Completed 1000 requests."
