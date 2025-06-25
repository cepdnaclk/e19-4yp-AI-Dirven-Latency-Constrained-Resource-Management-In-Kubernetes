# Stage 1: Builder
FROM golang:1.24.2 as builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .

# ✨ Cross-compile for Linux
RUN GOOS=linux GOARCH=amd64 go build -o echo-server main.go

# Stage 2: Minimal runtime image
FROM alpine:latest

# Ensure certs for HTTPS requests (optional for Prometheus metrics)
RUN apk --no-cache add ca-certificates

WORKDIR /root/
COPY --from=builder /app/echo-server .

EXPOSE 3002

CMD ["./echo-server"]
