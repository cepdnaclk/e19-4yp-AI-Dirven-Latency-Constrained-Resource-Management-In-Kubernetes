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

    @GetMapping("/n")
    public Map<String, Integer> getNthFibonacci(@RequestParam int n) {
        int result = fibonacci(n);
        Map<String, Integer> response = new HashMap<>();
        response.put("nthFibonacci", result);
        return response;
    }

    // Recursive Fibonacci function
    private int fibonacci(int n) {
        if (n <= 0) return 0;
        if (n == 1) return 1;
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
}
