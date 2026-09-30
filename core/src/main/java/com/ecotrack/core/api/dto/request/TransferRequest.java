package com.ecotrack.core.api.dto.request;

public record TransferRequest(String receiver, Double amount, String message, String tag) {}
