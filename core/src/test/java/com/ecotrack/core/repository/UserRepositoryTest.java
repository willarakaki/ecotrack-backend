package com.ecotrack.core.repository;

import com.ecotrack.core.config.AbstractIntegrationTest;
import com.ecotrack.core.domain.entity.Tenant;
import com.ecotrack.core.domain.entity.User;
import com.ecotrack.core.domain.enums.RoleType;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

class UserRepositoryTest extends AbstractIntegrationTest {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private TenantRepository tenantRepository;

    private Tenant activeTenant;

    @BeforeEach
    void setUp() {
        Tenant tenant = new Tenant();
        tenant.setCompanyName("EcoTech S.A.");
        tenant.setCnpj("98765432000111");
        activeTenant = tenantRepository.saveAndFlush(tenant);
    }

    @Test
    @DisplayName("Deve buscar o usuário respeitando o isolamento Multi-Tenant")
    void shouldFindUserByEmailAndTenantId() {
        // Arrange
        User user = new User();
        user.setTenant(activeTenant);
        user.setFullName("Colaborador Engajado"); // Base da força de trabalho[cite: 2]
        user.setEmail("colaborador@ecotech.com");
        user.setPasswordHash("hashed_secure_password");
        user.setRoleType(RoleType.EMPLOYEE);
        userRepository.saveAndFlush(user);

        // Act - Busca válida (Email correto + Tenant Correto)
        Optional<User> foundUser = userRepository.findByEmailAndTenantId("colaborador@ecotech.com", activeTenant.getId());

        // Act - Busca inválida (Tentativa de vazamento de dados de outro Tenant)
        Optional<User> wrongTenantUser = userRepository.findByEmailAndTenantId("colaborador@ecotech.com", 999L);

        // Assert
        assertThat(foundUser).isPresent();
        assertThat(foundUser.get().getExternalId()).isNotNull();
        assertThat(wrongTenantUser).isEmpty(); // Confirma a blindagem de isolamento corporativo
    }
}