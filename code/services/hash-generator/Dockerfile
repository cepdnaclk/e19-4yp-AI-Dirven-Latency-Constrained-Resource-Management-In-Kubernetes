# Use OpenJDK 17 slim as base image
FROM openjdk:17-jdk-slim

# Set working directory
WORKDIR /app

# Copy built jar into the image
COPY target/hash-generator-0.0.1-SNAPSHOT.jar app.jar

# Expose the application port
EXPOSE 3005

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
