package com.ecotrack.core.service;

import com.ecotrack.core.domain.entity.Tenant;
import com.ecotrack.core.exception.BusinessException;
import com.ecotrack.core.repository.TenantRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class TenantServiceTest {

    @Mock
    private TenantRepository tenantRepository;

    @InjectMocks
    private TenantService tenantService;

    @Test
    @DisplayName("Deve criar um Tenant corporativo com sucesso")
    void shouldCreateTenantSuccessfully() {
        Tenant tenant = new Tenant();
        tenant.setCnpj("12345678000199");

        when(tenantRepository.findByCnpj(anyString())).thenReturn(Optional.empty());
        when(tenantRepository.save(any(Tenant.class))).thenReturn(tenant);

        Tenant savedTenant = tenantService.createTenant(tenant);

        assertThat(savedTenant).isNotNull();
        verify(tenantRepository, times(1)).save(tenant);
    }

    @Test
    @DisplayName("Deve bloquear a criação de Tenant com CNPJ duplicado para garantir isolamento")
    void shouldThrowExceptionWhenCnpjAlreadyExists() {
        Tenant tenant = new Tenant();
        tenant.setCnpj("12345678000199");

        when(tenantRepository.findByCnpj(anyString())).thenReturn(Optional.of(tenant));

        assertThrows(BusinessException.class, () -> tenantService.createTenant(tenant));
        verify(tenantRepository, never()).save(any(Tenant.class));
    }
}