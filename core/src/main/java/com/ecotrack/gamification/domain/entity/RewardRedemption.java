package com.ecotrack.gamification.domain.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "tb_reward_redemption")
@Getter
@Setter
public class RewardRedemption {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "external_id", nullable = false, unique = true, updatable = false)
    private String externalId = UUID.randomUUID().toString();

    @Column(name = "user_external_id", nullable = false, updatable = false)
    private String userExternalId;

    @Column(name = "reward_type", nullable = false, updatable = false)
    private String rewardType;

    @Column(name = "coins_deducted", nullable = false, updatable = false)
    private Double coinsDeducted;

    @Column(name = "processed_at", nullable = false, updatable = false)
    private LocalDateTime processedAt = LocalDateTime.now();
}
