# Build Stage
FROM golang AS builder
WORKDIR /app

COPY go.mod .
COPY main.go .

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o app

# Run Stage
FROM alpine:latest
COPY --from=builder /app/app /app

EXPOSE 3002
ENTRYPOINT ["/app"]
