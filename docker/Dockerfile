# Python image from Docker Hub
FROM python:3.9

# Set the working directory in the container
WORKDIR /spotify-api

# Copy the dependencies from requirements into the container
COPY ../requirements.txt .

# Install this dependency to not store installed depedencies after 
# closing the container.
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code into container
COPY ../ . .

# Expose port to run app on
EXPOSE 8888

# Run command to start the FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]