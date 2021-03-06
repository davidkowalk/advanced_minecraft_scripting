#!/bin/bash

# Installation File For Linux
# ===========================

# Get current Directory
echo "Finding Executable Directory..."
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "Adding alias to startup file..."
STR="alias ams=\"python3 $DIR/src/ams_compiler.py\""
echo $STR >> ~/.bashrc

# Update Current Session
echo "Update Current Session"
alias ams="python3 $DIR/src/ams_compiler.py"

echo "==========="
echo "|| DONE! ||"
echo "==========="
echo ""
