package com.ecotrack.gamification.service;

import com.ecotrack.core.domain.entity.User;
import com.ecotrack.core.repository.UserRepository;
import com.ecotrack.gamification.domain.dto.RedemptionRequest;
import com.ecotrack.gamification.domain.dto.RedemptionResponse;
import com.ecotrack.gamification.domain.entity.RewardRedemption;
import com.ecotrack.gamification.repository.sql.RewardRedemptionRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Isolation;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
public class MarketplaceService {

    private static final Logger log = LoggerFactory.getLogger(MarketplaceService.class);
    private final UserRepository userRepository;
    private final RewardRedemptionRepository redemptionRepository;

    public MarketplaceService(UserRepository userRepository, RewardRedemptionRepository redemptionRepository) {
        this.userRepository = userRepository;
        this.redemptionRepository = redemptionRepository;
    }

    /**
     * Processa o resgate de recompensas garantindo integridade e bloqueio contra Double-Spending.
     * Transactional com isolation READ_COMMITTED + Optimistic Locking implicit.
     */
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public RedemptionResponse redeemReward(String userExternalId, RedemptionRequest request) {
        
        User user = userRepository.findByExternalId(userExternalId)
                .orElseThrow(() -> new IllegalArgumentException("Usuário não encontrado: " + userExternalId));

        if (user.getEcoCoinsBalance() < request.costCoins()) {
            log.warn("Tentativa de resgate falhou (Saldo Insuficiente). Usuário: {}, Saldo: {}, Custo: {}", 
                    userExternalId, user.getEcoCoinsBalance(), request.costCoins());
            throw new IllegalStateException("Saldo de EcoCoins insuficiente para este resgate.");
        }

        // 1. Deduz o saldo
        user.setEcoCoinsBalance(user.getEcoCoinsBalance() - request.costCoins());
        userRepository.save(user); // Aqui o Optimistic Locking protege contra saques paralelos

        // 2. Grava a trilha financeira (Audit do B2B)
        RewardRedemption redemption = new RewardRedemption();
        redemption.setUserExternalId(userExternalId);
        redemption.setRewardType(request.rewardType());
        redemption.setCoinsDeducted(request.costCoins());
        
        RewardRedemption savedRedemption = redemptionRepository.save(redemption);

        log.info("Resgate aprovado! Usuário {} resgatou {}. Saldo restante: {}", 
                userExternalId, request.rewardType(), user.getEcoCoinsBalance());

        return new RedemptionResponse(
                savedRedemption.getExternalId(),
                "APPROVED",
                user.getEcoCoinsBalance(),
                savedRedemption.getProcessedAt()
        );
    }
}
