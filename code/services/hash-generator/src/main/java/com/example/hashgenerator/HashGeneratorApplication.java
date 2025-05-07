package com.example.hashgenerator;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;

@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
public class HashGeneratorApplication {

	public static void main(String[] args) {
		SpringApplication.run(HashGeneratorApplication.class, args);
	}

}
