package main

import (
	"encoding/json"
	"net/http"
	"strconv"
	"time"
	"log"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

type EchoResponse struct {
	Message string `json:"message"`
}

// Prometheus metrics
var (
	requestsTotal = prometheus.NewCounter(
		prometheus.CounterOpts{
			Name: "echo_number_requests_total",
			Help: "Total number of /echoNumber requests",
		},
	)
	requestDuration = prometheus.NewHistogram(
		prometheus.HistogramOpts{
			Name:    "echo_number_request_duration_seconds",
			Help:    "Duration of /echoNumber handler in seconds",
			Buckets: prometheus.DefBuckets,
		},
	)
)

func init() {
	prometheus.MustRegister(requestsTotal)
	prometheus.MustRegister(requestDuration)
}

func main() {
	http.HandleFunc("/echoNumber", echoNumberHandler)
	http.Handle("/metrics", promhttp.Handler())
	log.Println("🚀 Server started on port 3002")
	http.ListenAndServe(":3002", nil)
}

func echoNumberHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	requestsTotal.Inc()

	numberParam := r.URL.Query().Get("number")
	number, err := strconv.Atoi(numberParam)
	if err != nil {
		http.Error(w, "Invalid number", http.StatusBadRequest)
		return
	}

	response := EchoResponse{
		Message: "your number is " + strconv.Itoa(number),
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)

	duration := time.Since(start).Seconds()
	requestDuration.Observe(duration)
}
