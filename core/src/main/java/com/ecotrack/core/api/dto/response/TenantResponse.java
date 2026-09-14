package com.ecotrack.core.api.dto.response;

import com.ecotrack.core.domain.entity.Tenant;

// Nunca expomos o ID numérico, apenas o UUID (externalId) para segurança
public record TenantResponse(String externalId, String companyName, String plan) {
    public static TenantResponse from(Tenant tenant) {
        return new TenantResponse(
                tenant.getExternalId(),
                tenant.getCompanyName(),
                tenant.getSubscriptionPlan().name()
        );
    }
}