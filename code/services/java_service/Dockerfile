# Use a lightweight Java runtime
FROM openjdk:17-jdk-slim

# Set the working directory
WORKDIR /app

# Copy the jar file into the container
COPY target/demo-0.0.1.jar app.jar

# Expose the port that the application runs on
EXPOSE 3001

# Command to run the application
ENTRYPOINT ["java", "-jar", "app.jar"]
