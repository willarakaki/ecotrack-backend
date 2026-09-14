package com.ecotrack.core.repository;

import com.ecotrack.core.config.AbstractIntegrationTest;
import com.ecotrack.core.domain.entity.Tenant;
import com.ecotrack.core.domain.enums.SubscriptionPlan;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DataIntegrityViolationException;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;

class TenantRepositoryTest extends AbstractIntegrationTest {

    @Autowired
    private TenantRepository tenantRepository;

    @Test
    @DisplayName("Deve salvar uma corporação com sucesso e gerar UUID e Datas de Auditoria")
    void shouldSaveTenantSuccessfully() {
        // Arrange
        Tenant tenant = new Tenant();
        tenant.setCompanyName("Tech Corp Sustentável");
        tenant.setCnpj("12345678000199");
        tenant.setSubscriptionPlan(SubscriptionPlan.ENTERPRISE); // Plano premium focado no CFO[cite: 2]

        // Act
        Tenant savedTenant = tenantRepository.saveAndFlush(tenant);

        // Assert
        assertThat(savedTenant.getId()).isNotNull();
        assertThat(savedTenant.getExternalId()).isNotNull(); // Prevenção IDOR (OWASP)
        assertThat(savedTenant.getCreatedAt()).isNotNull();
        assertThat(savedTenant.getUpdatedAt()).isNotNull();
    }

    @Test
    @DisplayName("Deve lançar exceção ao tentar salvar CNPJ duplicado (Integridade)")
    void shouldThrowExceptionWhenCnpjIsDuplicated() {
        // Arrange
        Tenant tenant1 = new Tenant();
        tenant1.setCompanyName("Empresa A");
        tenant1.setCnpj("00000000000191");
        tenantRepository.saveAndFlush(tenant1);

        Tenant tenant2 = new Tenant();
        tenant2.setCompanyName("Empresa B");
        tenant2.setCnpj("00000000000191"); // Mesmo CNPJ

        // Act & Assert
        assertThrows(DataIntegrityViolationException.class, () -> tenantRepository.saveAndFlush(tenant2));
    }
}