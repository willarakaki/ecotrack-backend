package com.ecotrack.gamification.repository.nosql;

import com.ecotrack.gamification.domain.document.EsgActionAuditLog;
import org.springframework.stereotype.Repository;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbTable;
import software.amazon.awssdk.enhanced.dynamodb.TableSchema;

import java.util.UUID;

@Repository
public class EsgActionAuditLogRepository {

    private final DynamoDbTable<EsgActionAuditLog> auditLogTable;

    public EsgActionAuditLogRepository(DynamoDbEnhancedClient enhancedClient) {
        this.auditLogTable = enhancedClient.table("esg_action_audit_log", TableSchema.fromBean(EsgActionAuditLog.class));
    }

    /**
     * Salva o log de auditoria no DynamoDB.
     * Operação de Append-Only (imutabilidade garantida pelo modelo de Event Sourcing).
     */
    public void save(EsgActionAuditLog log) {
        // Validação defensiva (OWASP) para garantir integridade do Event Sourcing
        if (log.getTenantId() == null || log.getTimestamp() == null) {
            throw new IllegalArgumentException("TenantId e Timestamp são obrigatórios para a trilha de auditoria ESG.");
        }
        
        auditLogTable.putItem(log);
    }
    
    // Possíveis métodos de consulta futuros para relatórios de emissões / Extratos.
}
