# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Copy the initialization script into the container
COPY init_es_state.sh /usr/local/bin/init_es_state.sh

# Make the script executable
RUN chmod +x /usr/local/bin/init_es_state.sh

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the initialization script as the entrypoint
ENTRYPOINT ["/usr/local/bin/init_es_state.sh"]

# Run etl_script.py when the container launches
CMD ["python", "etl_script.py"]
