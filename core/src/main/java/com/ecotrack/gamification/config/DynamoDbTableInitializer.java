package com.ecotrack.gamification.config;

import com.ecotrack.gamification.domain.document.EsgActionAuditLog;
import jakarta.annotation.PostConstruct;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbTable;
import software.amazon.awssdk.enhanced.dynamodb.TableSchema;
import software.amazon.awssdk.services.dynamodb.model.ResourceInUseException;

@Configuration
@Profile({"dev", "test"})
public class DynamoDbTableInitializer {

    private final DynamoDbEnhancedClient enhancedClient;

    public DynamoDbTableInitializer(DynamoDbEnhancedClient enhancedClient) {
        this.enhancedClient = enhancedClient;
    }

    @PostConstruct
    public void createTableIfNotExists() {
        try {
            DynamoDbTable<EsgActionAuditLog> table = enhancedClient.table("esg_action_audit_log", TableSchema.fromBean(EsgActionAuditLog.class));
            table.createTable();
        } catch (ResourceInUseException e) {
            // Tabela já existe, o que é o comportamento esperado após a primeira execução
        }
    }
}
