FROM python:3.11

# Doing some repositories update
RUN pip install --upgrade pip

WORKDIR /
ENV PYTHONPATH=/app

# Copying the app in the Python base image
COPY ./app /app

# Install required libraries at latest version as possible, just for simplicity
# But they're version should be fixed normally
RUN pip install -r /app/requirements.txt

# Running automated tests to be sure the code works as expected
RUN pytest /app

EXPOSE 8000
# the command to run the application, when the Docker container starts
CMD ["python", "/app/app.py"]