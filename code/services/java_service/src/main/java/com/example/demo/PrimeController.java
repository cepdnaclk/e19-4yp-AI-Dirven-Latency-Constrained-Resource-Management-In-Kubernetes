package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PrimeController {

    @GetMapping("/isPrime")
    public PrimeResponse isPrime(@RequestParam int number) {
        boolean result = isPrimeRecursive(number, 2);
        return new PrimeResponse(number, result);
    }

    private boolean isPrimeRecursive(int number, int divisor) {
        if (number <= 1) {
            return false;
        }
        if (divisor * divisor > number) {
            return true;
        }
        if (number % divisor == 0) {
            return false;
        }
        return isPrimeRecursive(number, divisor + 1);
    }

    static class PrimeResponse {
        private int number;
        private boolean prime;

        public PrimeResponse(int number, boolean prime) {
            this.number = number;
            this.prime = prime;
        }

        public int getNumber() {
            return number;
        }

        public boolean isPrime() {
            return prime;
        }
    }
}
