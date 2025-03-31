#!/bin/bash
# Simple script to compile core.c into a shared library

# Get the directory where the script resides
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
OUTPUT_NAME="core.so" # Use .dll for Windows

echo "Compiling core.c into ${OUTPUT_NAME}..."

# Compile using gcc with standard C99, creating a position-independent shared object
gcc -shared -o "$DIR/${OUTPUT_NAME}" -fPIC "$DIR/core.c" -std=c99

if [ $? -eq 0 ]; then
  echo "Compilation successful: ${OUTPUT_NAME} created in $DIR"
else
  echo "Compilation failed."
  exit 1
fi

exit 0