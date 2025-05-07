# Use OpenJDK 17 as the base image
FROM openjdk:17-jdk-slim

# Set the working directory in the container
WORKDIR /app

# Copy the built jar into the container
COPY target/base64-encoder-0.0.1-SNAPSHOT.jar app.jar

# Expose port 3004
EXPOSE 3004

# Run the Spring Boot application
ENTRYPOINT ["java", "-jar", "app.jar"]
