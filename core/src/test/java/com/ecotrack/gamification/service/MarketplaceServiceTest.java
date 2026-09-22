package com.ecotrack.gamification.service;

import com.ecotrack.core.domain.entity.User;
import com.ecotrack.core.repository.UserRepository;
import com.ecotrack.gamification.domain.dto.RedemptionRequest;
import com.ecotrack.gamification.domain.dto.RedemptionResponse;
import com.ecotrack.gamification.domain.entity.RewardRedemption;
import com.ecotrack.gamification.repository.sql.RewardRedemptionRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class MarketplaceServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private RewardRedemptionRepository redemptionRepository;

    @InjectMocks
    private MarketplaceService marketplaceService;

    @Test
    @DisplayName("Deve realizar resgate com sucesso e deduzir saldo do usuário")
    void shouldRedeemRewardSuccessfully() {
        // Arrange
        String userExternalId = UUID.randomUUID().toString();
        User mockUser = new User();
        mockUser.setExternalId(userExternalId);
        mockUser.setEcoCoinsBalance(150.0); // Saldo suficiente

        RedemptionRequest request = new RedemptionRequest("VOUCHER_IFOOD_50", 100.0);
        
        RewardRedemption mockSavedRedemption = new RewardRedemption();
        mockSavedRedemption.setExternalId(UUID.randomUUID().toString());

        when(userRepository.findByExternalId(userExternalId)).thenReturn(Optional.of(mockUser));
        when(redemptionRepository.save(any(RewardRedemption.class))).thenReturn(mockSavedRedemption);

        // Act
        RedemptionResponse response = marketplaceService.redeemReward(userExternalId, request);

        // Assert
        assertThat(response.status()).isEqualTo("APPROVED");
        assertThat(response.remainingBalance()).isEqualTo(50.0); // 150 - 100

        // Verifica chamadas transacionais
        verify(userRepository, times(1)).save(mockUser);
        
        // Verifica dados de auditoria
        ArgumentCaptor<RewardRedemption> redemptionCaptor = ArgumentCaptor.forClass(RewardRedemption.class);
        verify(redemptionRepository).save(redemptionCaptor.capture());
        RewardRedemption capturedRedemption = redemptionCaptor.getValue();
        
        assertThat(capturedRedemption.getUserExternalId()).isEqualTo(userExternalId);
        assertThat(capturedRedemption.getCoinsDeducted()).isEqualTo(100.0);
        assertThat(capturedRedemption.getRewardType()).isEqualTo("VOUCHER_IFOOD_50");
    }

    @Test
    @DisplayName("Deve bloquear resgate e lançar exceção quando o saldo for insuficiente")
    void shouldBlockRedemptionWhenBalanceIsInsufficient() {
        // Arrange
        String userExternalId = UUID.randomUUID().toString();
        User mockUser = new User();
        mockUser.setExternalId(userExternalId);
        mockUser.setEcoCoinsBalance(30.0); // Saldo Insuficiente

        RedemptionRequest request = new RedemptionRequest("VOUCHER_FLASH_100", 100.0);

        when(userRepository.findByExternalId(userExternalId)).thenReturn(Optional.of(mockUser));

        // Act & Assert
        IllegalStateException exception = assertThrows(IllegalStateException.class, () -> {
            marketplaceService.redeemReward(userExternalId, request);
        });

        assertThat(exception.getMessage()).contains("Saldo de EcoCoins insuficiente");
        
        // Garante que nenhuma dedução ou auditoria foi salva
        verify(userRepository, never()).save(any(User.class));
        verify(redemptionRepository, never()).save(any(RewardRedemption.class));
    }
}
