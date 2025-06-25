# Use official Golang image as builder
FROM golang:1.24.2 AS builder

WORKDIR /app

# Copy and download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the Go app
RUN go build -o echo-server .

# Use a minimal image for runtime
FROM alpine:latest

WORKDIR /root/

# Copy the binary from builder
COPY --from=builder /app/echo-server .

# Expose the service port
EXPOSE 3002

# Run the binary
CMD ["./echo-server"]
