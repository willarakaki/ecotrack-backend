package com.ecotrack.core.config;

// Novos imports do Spring Boot 4.x
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jdbc.test.autoconfigure.AutoConfigureTestDatabase;

import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.OracleContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import org.springframework.context.annotation.Import;

import org.testcontainers.containers.GenericContainer;
import org.testcontainers.utility.DockerImageName;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(JpaConfig.class)
public abstract class AbstractIntegrationTest {

    protected static final OracleContainer oracleContainer = new OracleContainer("gvenzl/oracle-xe:21-slim-faststart")
            .withDatabaseName("ecotrack_test")
            .withUsername("test_user")
            .withPassword("test_pass");

    // Usando amazon/dynamodb-local para evitar erros de Docker Socket no Windows (LocalStack exige socket bind)
    protected static final GenericContainer<?> dynamoDbContainer = new GenericContainer<>(DockerImageName.parse("amazon/dynamodb-local:latest"))
            .withExposedPorts(8000);

    static {
        oracleContainer.start();
        dynamoDbContainer.start();
    }

    @DynamicPropertySource
    static void setProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", oracleContainer::getJdbcUrl);
        registry.add("spring.datasource.username", oracleContainer::getUsername);
        registry.add("spring.datasource.password", oracleContainer::getPassword);
        registry.add("spring.jpa.hibernate.ddl-auto", () -> "create-drop");

        // Configurações do AWS SDK v2 para apontar para o DynamoDB Local
        registry.add("aws.dynamodb.endpoint", () -> "http://" + dynamoDbContainer.getHost() + ":" + dynamoDbContainer.getMappedPort(8000));
        registry.add("aws.region", () -> "us-east-1");
        registry.add("aws.accessKeyId", () -> "fakeMyKeyId");
        registry.add("aws.secretAccessKey", () -> "fakeSecretAccessKey");
    }
}