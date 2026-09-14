package com.ecotrack.core.repository;

import com.ecotrack.core.domain.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    Optional<User> findByExternalId(String externalId);

    // Método crítico para isolamento Multi-Tenant em consultas corporativas
    Optional<User> findByEmailAndTenantId(String email, Long tenantId);
}