package com.ecotrack.core.service;

import com.ecotrack.core.domain.entity.Tenant;
import com.ecotrack.core.exception.BusinessException;
import com.ecotrack.core.repository.TenantRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class TenantService {

    private final TenantRepository tenantRepository;

    @Transactional
    public Tenant createTenant(Tenant tenant) {
        if (tenantRepository.findByCnpj(tenant.getCnpj()).isPresent()) {
            throw new BusinessException("Já existe uma corporação registrada com este CNPJ.");
        }

        // Regras adicionais de Setup Enterprise podem ser injetadas aqui futuramente
        return tenantRepository.save(tenant);
    }
}