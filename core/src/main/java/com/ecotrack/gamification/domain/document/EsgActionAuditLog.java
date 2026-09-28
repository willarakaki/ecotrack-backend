package com.ecotrack.gamification.domain.document;

import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbBean;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbPartitionKey;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbSortKey;

import java.time.Instant;
import java.util.UUID;

@DynamoDbBean
public class EsgActionAuditLog {

    private UUID tenantId;
    private Instant timestamp;
    private UUID actionId;
    private UUID userId;
    private String actionType; // ex: "MOBILIDADE_VERDE", "SYSTEM_MESSAGE", "PEER_PRAISE_SENT"
    private double estimatedCo2Saved;
    
    // Novos campos Sociais / Feed (Adicionados para o Frontend)
    private String authorName;
    private String content;
    private String tag;
    private int likesCount;

    // Construtor vazio obrigatorio para o AWS SDK
    public EsgActionAuditLog() {}

    @DynamoDbPartitionKey
    public UUID getTenantId() { return tenantId; }
    public void setTenantId(UUID tenantId) { this.tenantId = tenantId; }

    @DynamoDbSortKey
    public Instant getTimestamp() { return timestamp; }
    public void setTimestamp(Instant timestamp) { this.timestamp = timestamp; }

    public UUID getActionId() { return actionId; }
    public void setActionId(UUID actionId) { this.actionId = actionId; }

    public UUID getUserId() { return userId; }
    public void setUserId(UUID userId) { this.userId = userId; }

    public String getActionType() { return actionType; }
    public void setActionType(String actionType) { this.actionType = actionType; }

    public double getEstimatedCo2Saved() { return estimatedCo2Saved; }
    public void setEstimatedCo2Saved(double estimatedCo2Saved) { this.estimatedCo2Saved = estimatedCo2Saved; }

    public String getAuthorName() { return authorName; }
    public void setAuthorName(String authorName) { this.authorName = authorName; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public String getTag() { return tag; }
    public void setTag(String tag) { this.tag = tag; }

    public int getLikesCount() { return likesCount; }
    public void setLikesCount(int likesCount) { this.likesCount = likesCount; }
}
