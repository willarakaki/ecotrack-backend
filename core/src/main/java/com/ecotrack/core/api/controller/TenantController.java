package com.ecotrack.core.api.controller;

import com.ecotrack.core.api.dto.request.TenantRequest;
import com.ecotrack.core.api.dto.response.TenantResponse;
import com.ecotrack.core.domain.entity.Tenant;
import com.ecotrack.core.service.TenantService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import java.net.URI;

@RestController
@RequestMapping("/api/v1/tenants")
@RequiredArgsConstructor
public class TenantController {

    private final TenantService tenantService;

    @PostMapping
    public ResponseEntity<TenantResponse> createTenant(@Valid @RequestBody TenantRequest request) {
        Tenant savedTenant = tenantService.createTenant(request.toEntity());
        TenantResponse response = TenantResponse.from(savedTenant);

        // Retorna HTTP 201 com o cabeçalho Location (Padrão REST de Maturidade Richardson)
        URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}")
                .buildAndExpand(response.externalId())
                .toUri();

        return ResponseEntity.created(location).body(response);
    }
}