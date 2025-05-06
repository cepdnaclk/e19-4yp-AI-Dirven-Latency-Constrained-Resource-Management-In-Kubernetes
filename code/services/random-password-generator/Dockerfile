# Use OpenJDK 17 as the base image
FROM openjdk:17-jdk-slim

# Set the working directory in the container
WORKDIR /app

# Copy the built jar into the container
COPY target/random-password-generator-0.0.1-SNAPSHOT.jar app.jar

# Expose port 3003
EXPOSE 3003

# Run the Spring Boot application on port 3003
ENTRYPOINT ["java", "-jar", "app.jar", "--server.port=3003"]
