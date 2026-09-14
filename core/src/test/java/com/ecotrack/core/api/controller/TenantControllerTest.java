package com.ecotrack.core.api.controller;

import com.ecotrack.core.domain.entity.Tenant;
import com.ecotrack.core.service.TenantService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(TenantController.class)
class TenantControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private TenantService tenantService;

    @Test
    @DisplayName("Deve retornar 201 Created ao enviar payload válido para corporação")
    void shouldReturn201WhenPayloadIsValid() throws Exception {
        Tenant mockTenant = new Tenant();
        mockTenant.setExternalId(UUID.randomUUID().toString());
        mockTenant.setCompanyName("EcoTech B2B");
        mockTenant.setSubscriptionPlan(com.ecotrack.core.domain.enums.SubscriptionPlan.ENTERPRISE);

        when(tenantService.createTenant(any(Tenant.class))).thenReturn(mockTenant);

        String validPayload = """
                {
                    "companyName": "EcoTech B2B",
                    "cnpj": "12345678000199",
                    "subscriptionPlan": "ENTERPRISE"
                }
                """;

        mockMvc.perform(post("/api/v1/tenants")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(validPayload))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.externalId").exists())
                .andExpect(jsonPath("$.companyName").value("EcoTech B2B"));
    }

    @Test
    @DisplayName("Deve retornar 400 Bad Request se CNPJ estiver em formato inválido")
    void shouldReturn400WhenCnpjIsInvalid() throws Exception {
        String invalidPayload = """
                {
                    "companyName": "EcoTech B2B",
                    "cnpj": "CNPJ_INVALIDO_TEXTO",
                    "subscriptionPlan": "STANDARD"
                }
                """;

        mockMvc.perform(post("/api/v1/tenants")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(invalidPayload))
                .andExpect(status().isBadRequest());
    }
}