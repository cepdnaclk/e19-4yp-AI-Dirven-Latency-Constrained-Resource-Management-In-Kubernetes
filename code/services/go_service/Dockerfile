# Build Stage
FROM golang:latest AS builder
WORKDIR /app

# Copy Go mod and sum files
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy the source code
COPY main.go .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o app .
# Run Stage
FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/app .

CMD ["./app"]

