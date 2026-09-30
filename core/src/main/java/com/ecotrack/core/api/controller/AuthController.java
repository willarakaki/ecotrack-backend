package com.ecotrack.core.api.controller;

import com.ecotrack.core.domain.entity.User;
import com.ecotrack.core.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class AuthController {

    private final UserRepository userRepository;
    private final org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder passwordEncoder = new org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder();

    @PostMapping("/login")
    @Transactional(readOnly = true)
    public ResponseEntity<?> login(@RequestBody Map<String, String> credentials) {
        String email = credentials.get("email");
        String password = credentials.get("password");

        if (email == null || password == null) {
            return ResponseEntity.badRequest().body(Map.of("message", "Email e senha sao obrigatorios."));
        }

        User user = userRepository.findByEmail(email).orElse(null);

        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("message", "E-mail ou senha incorretos."));
        }

        // Aceitamos "senha123" pelo mock do V4 ou valida via passwordEncoder
        if (!"senha123".equals(password) && !passwordEncoder.matches(password, user.getPasswordHash())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("message", "E-mail ou senha incorretos."));
        }

        return ResponseEntity.ok(Map.of(
            "token", "mock-jwt-token-" + user.getExternalId(),
            "userId", user.getExternalId(),
            "tenantId", user.getTenant().getExternalId(),
            "role", user.getRoleType().name(),
            "name", user.getFullName(),
            "email", user.getEmail(),
            "ecoCoins", user.getEcoCoinsBalance(),
            "totalCo2Saved", user.getTotalCo2Saved()
        ));
    }
}
