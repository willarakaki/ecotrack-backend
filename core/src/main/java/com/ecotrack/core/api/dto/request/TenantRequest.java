package com.ecotrack.core.api.dto.request;

import com.ecotrack.core.domain.entity.Tenant;
import com.ecotrack.core.domain.enums.SubscriptionPlan;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;

public record TenantRequest(
        @NotBlank(message = "O nome da empresa é obrigatório.")
        String companyName,

        @NotBlank(message = "O CNPJ é obrigatório.")
        @Pattern(regexp = "\\d{14}", message = "O CNPJ deve conter exatamente 14 dígitos numéricos.")
        String cnpj,

        @NotNull(message = "O plano de assinatura deve ser informado.")
        SubscriptionPlan subscriptionPlan
) {
    public Tenant toEntity() {
        Tenant tenant = new Tenant();
        tenant.setCompanyName(this.companyName);
        tenant.setCnpj(this.cnpj);
        tenant.setSubscriptionPlan(this.subscriptionPlan);
        return tenant;
    }
}