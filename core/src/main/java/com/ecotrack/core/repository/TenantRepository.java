package com.ecotrack.core.repository;

import com.ecotrack.core.domain.entity.Tenant;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface TenantRepository extends JpaRepository<Tenant, Long> {
    Optional<Tenant> findByCnpj(String cnpj);
    Optional<Tenant> findByExternalId(String externalId);
}