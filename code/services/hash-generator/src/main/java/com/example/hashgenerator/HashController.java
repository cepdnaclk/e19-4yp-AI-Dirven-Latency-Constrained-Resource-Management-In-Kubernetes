package com.example.hashgenerator;

import com.example.hashgenerator.HashService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/hash")
public class HashController {

    @Autowired
    private HashService hashService;

    @PostMapping("/sha256")
    public String getSHA256Hash(@RequestBody String input) {
        return hashService.generateSHA256Hash(input);
    }
}
