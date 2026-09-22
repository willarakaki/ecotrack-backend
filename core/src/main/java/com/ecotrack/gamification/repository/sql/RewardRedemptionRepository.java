package com.ecotrack.gamification.repository.sql;

import com.ecotrack.gamification.domain.entity.RewardRedemption;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface RewardRedemptionRepository extends JpaRepository<RewardRedemption, Long> {
}
