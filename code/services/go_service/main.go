package main

import (
	"encoding/json"
	"net/http"
	"strconv"
)

type PrimeResponse struct {
	Number int  `json:"number"`
	Prime  bool `json:"prime"`
}

func main() {
	http.HandleFunc("/isPrime", isPrimeHandler)

	// Start server on port 8080
	http.ListenAndServe(":8080", nil)
}

func isPrimeHandler(w http.ResponseWriter, r *http.Request) {
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
