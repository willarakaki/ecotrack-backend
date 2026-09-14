package com.ecotrack.core.messaging.publisher;

import com.ecotrack.core.messaging.event.EvidenceSubmittedEvent;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.apache.kafka.common.TopicPartition;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;

import java.time.Instant;
import java.util.concurrent.CompletableFuture;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class EvidencePublisherTest {

    @Mock
    private KafkaTemplate<String, Object> kafkaTemplate;

    @InjectMocks
    private EvidencePublisher evidencePublisher;

    @Test
    @DisplayName("Deve publicar evento de evidência com sucesso assincronamente")
    void shouldPublishEvidenceEventSuccessfully() {
        // Arrange
        EvidenceSubmittedEvent event = new EvidenceSubmittedEvent(
                "evt-123", "tenant-456", "user-789", "s3://bucket/img.jpg", "DESLOCAMENTO", Instant.now()
        );

        TopicPartition topicPartition = new TopicPartition("evidence.submitted.v1", 0);

        // CORREÇÃO: Assinatura do Kafka 3.x+ (Exatamente 6 argumentos, com tipagem int/long correta)
        RecordMetadata metadata = new RecordMetadata(
                topicPartition,
                0L, // baseOffset (long)
                0,  // batchIndex (int)
                System.currentTimeMillis(), // timestamp (long)
                0,  // serializedKeySize (int)
                0   // serializedValueSize (int)
        );

        SendResult<String, Object> sendResult = new SendResult<>(
                new ProducerRecord<>("evidence.submitted.v1", event), metadata
        );

        when(kafkaTemplate.send(anyString(), anyString(), any()))
                .thenReturn(CompletableFuture.completedFuture(sendResult));

        // Act
        evidencePublisher.publish(event);

        // Assert
        verify(kafkaTemplate, times(1)).send(eq("evidence.submitted.v1"), eq("evt-123"), eq(event));
    }

    @Test
    @DisplayName("Deve tratar falha no envio assíncrono sem quebrar a thread principal")
    void shouldHandleAsyncPublishFailureGracefully() {
        // Arrange
        EvidenceSubmittedEvent event = new EvidenceSubmittedEvent(
                "evt-999", "tenant-456", "user-789", "s3://bucket/img.jpg", "RECICLAGEM", Instant.now()
        );

        // Simula uma queda abrupta de rede ou indisponibilidade do broker Kafka
        when(kafkaTemplate.send(anyString(), anyString(), any()))
                .thenReturn(CompletableFuture.failedFuture(new RuntimeException("Kafka Broker Indisponível")));

        // Act
        evidencePublisher.publish(event);

        // Assert
        verify(kafkaTemplate, times(1)).send(eq("evidence.submitted.v1"), eq("evt-999"), eq(event));
        // O teste passa se a exceção for silenciosamente tratada pelo log no callback,
        // garantindo que não vaze para o Controller HTTP (Proteção Anti-Loop de tela).
    }
}