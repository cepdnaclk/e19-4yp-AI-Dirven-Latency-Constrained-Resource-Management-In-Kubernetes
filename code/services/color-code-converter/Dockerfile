# Use a lightweight Java runtime
FROM openjdk:17-jdk-slim

# Set the working directory
WORKDIR /app

# Copy the jar file into the container
COPY target/color-0.0.1-SNAPSHOT.jar app.jar

# Expose the port that the application runs on
EXPOSE 3015

# Command to run the application
ENTRYPOINT ["java", "-jar", "app.jar", "--server.port=3015"]
