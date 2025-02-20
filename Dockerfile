# Use Python base image
FROM python:3.10

# Install OpenJDK 17
RUN apt-get update && apt-get install -y openjdk-17-jdk

# Set Java path
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Install dependencies
RUN pip install fastapi timefold uvicorn pydantic datetime

# Expose port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]