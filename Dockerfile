# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
# Install pip in upgrade mode and kuksa-client globally
RUN pip install --upgrade pip && \
    pip install --no-cache-dir kuksa-client

# Create necessary directory structure
RUN mkdir -p /app/src

# Copy application code
COPY src/zonal_app.py /app/src/zonal_app.py
COPY src/can_driver.py /app/src/can_driver.py
COPY src/libcontrolcanfd.so /app/src/libcontrolcanfd.so

# Make port 80 available to the world outside this container
EXPOSE 80

# Set the entrypoint and command
ENTRYPOINT ["python", "src/zonal_app.py"]
CMD ["-loopback=0","192.168.1.1:55555"]