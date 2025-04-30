package com.example.demo;

import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@RestController
public class MetricsRedirectController {

    private final RestTemplate restTemplate = new RestTemplate();

    @GetMapping("/metrics")
    public ResponseEntity<String> proxyPrometheusMetrics() {
        String metricsData = restTemplate.getForObject("http://localhost:3001/actuator/prometheus", String.class);
        return ResponseEntity.ok(metricsData);
    }
}
