package com.ecotrack.gamification.service;

import com.ecotrack.core.domain.entity.User;
import com.ecotrack.core.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Isolation;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
public class GamificationEngineService {

    private static final Logger log = LoggerFactory.getLogger(GamificationEngineService.class);
    private final UserRepository userRepository;

    // Constante de conversão: Exemplo - 1 kg de CO2 poupado = 10 EcoCoins
    private static final double ECO_COINS_PER_KG_CO2 = 10.0;

    public GamificationEngineService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    /**
     * Processa a recompensa do usuário de forma atômica e segura.
     * Transactional com nível Read Committed e controle de concorrência via Optimistic Locking (@Version no User).
     */
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public void processReward(UUID userExternalId, double estimatedCo2Saved) {
        if (estimatedCo2Saved <= 0) {
            log.debug("Nenhuma recompensa aplicável (CO2 <= 0) para o usuário: {}", userExternalId);
            return;
        }

        // Recupera usuário (o UserRepository padrão deve ter um findByExternalId)
        User user = userRepository.findByExternalId(userExternalId.toString())
                .orElseThrow(() -> new IllegalArgumentException("Usuário não encontrado para processamento de recompensas: " + userExternalId));

        // Calcula EcoCoins e atualiza saldos
        double earnedCoins = estimatedCo2Saved * ECO_COINS_PER_KG_CO2;
        
        user.setEcoCoinsBalance(user.getEcoCoinsBalance() + earnedCoins);
        user.setTotalCo2Saved(user.getTotalCo2Saved() + estimatedCo2Saved);

        userRepository.save(user); // Optimistic Locking atuará aqui

        log.info("Recompensa processada: Usuário {} ganhou {} EcoCoins por economizar {} kg de CO2",
                userExternalId, earnedCoins, estimatedCo2Saved);
    }
}
