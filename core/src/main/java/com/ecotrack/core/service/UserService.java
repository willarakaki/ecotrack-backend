package com.ecotrack.core.service;

import com.ecotrack.core.domain.entity.Tenant;
import com.ecotrack.core.domain.entity.User;
import com.ecotrack.core.exception.BusinessException;
import com.ecotrack.core.repository.TenantRepository;
import com.ecotrack.core.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final TenantRepository tenantRepository;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @Transactional
    public User createUser(User user, Long tenantId) {
        Tenant tenant = tenantRepository.findById(tenantId)
                .orElseThrow(() -> new BusinessException("Corporação não encontrada. Operação bloqueada."));

        if (!tenant.getIsActive()) {
            throw new BusinessException("A corporação vinculada está inativa.");
        }

        if (userRepository.findByEmail(user.getEmail()).isPresent()) {
            throw new BusinessException("E-mail corporativo já cadastrado.");
        }

        user.setTenant(tenant);
        user.setPasswordHash(passwordEncoder.encode(user.getPasswordHash()));

        return userRepository.save(user);
    }
}