package com.example.base64encoder;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import java.util.Base64;

@RestController
@RequestMapping("/base64")
public class Base64Controller {

    @GetMapping("/encode")
    public String encode(@RequestParam String input) {
        return Base64.getEncoder().encodeToString(input.getBytes());
    }

    @GetMapping("/decode")
    public String decode(@RequestParam String input) {
        byte[] decodedBytes = Base64.getDecoder().decode(input);
        return new String(decodedBytes);
    }
}
