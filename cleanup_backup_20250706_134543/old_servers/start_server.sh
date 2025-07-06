#!/bin/bash

# Activate the Conda environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate news_feed_env

# Get the path to the python executable in the activated environment
PYTHON_EXEC=$(which python)

# Install dependencies (if not already installed) using the environment's python
"$PYTHON_EXEC" -m pip install -r requirements.txt
"$PYTHON_EXEC" -m pip install gunicorn # Ensure gunicorn is installed in the environment

# Run the web server using gunicorn as a Python module on port 8081
"$PYTHON_EXEC" -m gunicorn -w 1 src.web_news_app:app -b 127.0.0.1:8081
