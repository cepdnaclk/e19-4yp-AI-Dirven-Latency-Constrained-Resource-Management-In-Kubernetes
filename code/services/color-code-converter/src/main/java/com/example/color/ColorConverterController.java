package com.example.color;
import org.springframework.web.bind.annotation.*;
import java.awt.Color;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/color")
public class ColorConverterController {

    // Convert HEX to RGB
    @GetMapping("/hex-to-rgb")
    public Map<String, Object> hexToRgb(@RequestParam String hex) {
        Color color = Color.decode(hex);
        Map<String, Object> result = new HashMap<>();
        result.put("red", color.getRed());
        result.put("green", color.getGreen());
        result.put("blue", color.getBlue());
        return result;
    }

    // Convert RGB to HEX
    @GetMapping("/rgb-to-hex")
    public Map<String, String> rgbToHex(
            @RequestParam int r,
            @RequestParam int g,
            @RequestParam int b) {
        String hex = String.format("#%02x%02x%02x", r, g, b);
        Map<String, String> result = new HashMap<>();
        result.put("hex", hex);
        return result;
    }

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
