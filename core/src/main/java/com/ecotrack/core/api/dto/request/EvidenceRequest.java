package com.ecotrack.core.api.dto.request;

import java.util.Map;

public record EvidenceRequest(
        String activityType,
        Map<String, Object> metadata,
        String evidenceUrl
) {}
