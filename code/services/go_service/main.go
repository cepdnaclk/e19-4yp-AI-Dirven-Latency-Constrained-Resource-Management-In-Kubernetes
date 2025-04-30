package main

import (
	"encoding/json"
	"net/http"
	"strconv"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

type PrimeResponse struct {
	Number int  `json:"number"`
	Prime  bool `json:"prime"`
}

// Prometheus metrics
var (
	requestsTotal = prometheus.NewCounter(
		prometheus.CounterOpts{
			Name: "prime_checker_requests_total",
			Help: "Total number of /isPrime requests",
		},
	)
	requestDuration = prometheus.NewHistogram(
		prometheus.HistogramOpts{
			Name:    "prime_checker_request_duration_seconds",
			Help:    "Duration of /isPrime handler in seconds",
			Buckets: prometheus.DefBuckets,
		},
	)
)

func init() {
	prometheus.MustRegister(requestsTotal)
	prometheus.MustRegister(requestDuration)
}

func main() {
	http.HandleFunc("/isPrime", isPrimeHandler)

	// Prometheus endpoint for metrics
	http.Handle("/metrics", promhttp.Handler())

	// Start server on port 3002
	http.ListenAndServe(":3002", nil)
}

func isPrimeHandler(w http.ResponseWriter, r *http.Request) {
	start := time.Now()
	requestsTotal.Inc()

	numberParam := r.URL.Query().Get("number")
	number, err := strconv.Atoi(numberParam)
	if err != nil {
		http.Error(w, "Invalid number", http.StatusBadRequest)
		return
	}

	result := isPrimeRecursive(number, 2)

	response := PrimeResponse{
		Number: number,
		Prime:  result,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)

	duration := time.Since(start).Seconds()
	requestDuration.Observe(duration)
}

func isPrimeRecursive(number int, divisor int) bool {
	if number <= 1 {
		return false
	}
	if divisor*divisor > number {
		return true
	}
	if number%divisor == 0 {
		return false
	}
	return isPrimeRecursive(number, divisor+1)
}
