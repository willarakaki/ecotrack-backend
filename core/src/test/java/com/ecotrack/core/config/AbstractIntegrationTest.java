package com.ecotrack.core.config;

import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.OracleContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

@DataJpaTest
@Testcontainers
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE) // Força o uso do Oracle, desabilita H2
public abstract class AbstractIntegrationTest {

    // Sobe um contêiner Docker do Oracle leve especificamente para os testes
    @Container
    protected static final OracleContainer oracleContainer = new OracleContainer("gvenzl/oracle-xe:21-slim-faststart")
            .withDatabaseName("ecotrack_test")
            .withUsername("test_user")
            .withPassword("test_pass");

    @DynamicPropertySource
    static void setProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", oracleContainer::getJdbcUrl);
        registry.add("spring.datasource.username", oracleContainer::getUsername);
        registry.add("spring.datasource.password", oracleContainer::getPassword);
        // O Flyway rodará automaticamente os scripts V1 ao detectar o datasource
    }
}
