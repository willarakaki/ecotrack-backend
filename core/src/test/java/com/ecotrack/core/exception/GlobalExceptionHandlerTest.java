package com.ecotrack.core.exception;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.ProblemDetail;
import org.springframework.validation.BindingResult;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class GlobalExceptionHandlerTest {

    @InjectMocks
    private GlobalExceptionHandler exceptionHandler;

    @Test
    @DisplayName("Deve retornar ProblemDetail HTTP 422 para BusinessException")
    void shouldHandleBusinessException() {
        BusinessException ex = new BusinessException("CNPJ já cadastrado.");
        ProblemDetail response = exceptionHandler.handleBusinessException(ex);

        // Uso direto do código inteiro para evitar a depreciação do HttpStatus
        assertThat(response.getStatus()).isEqualTo(422);
        assertThat(response.getDetail()).isEqualTo("CNPJ já cadastrado.");
        assertThat(response.getTitle()).isEqualTo("Violação de Regra de Negócio");
    }

    @Test
    @DisplayName("Deve mascarar stack trace e retornar HTTP 500 genérico para exceções não mapeadas")
    void shouldMaskStacktraceOnGenericException() {
        Exception ex = new RuntimeException("Falha catastrófica!");
        ProblemDetail response = exceptionHandler.handleAllUncaughtException(ex);

        assertThat(response.getStatus()).isEqualTo(500); // Uso direto do 500
        assertThat(response.getDetail()).doesNotContain("Falha");
    }

    @Test
    @DisplayName("Deve extrair lista de campos inválidos para MethodArgumentNotValidException")
    void shouldHandleValidationException() {
        // 1. Restauração do Mock setup (A variável 'ex' precisa existir no escopo)
        MethodArgumentNotValidException ex = mock(MethodArgumentNotValidException.class);
        BindingResult bindingResult = mock(BindingResult.class);

        FieldError fieldError = new FieldError("tenantRequest", "cnpj", "O CNPJ deve conter exatamente 14 dígitos numéricos.");

        // 2. Configurando o comportamento do Mock
        when(ex.getBindingResult()).thenReturn(bindingResult);
        when(bindingResult.getAllErrors()).thenReturn(List.of(fieldError));

        // 3. Chamando o método com a variável 'ex' agora existente
        ProblemDetail response = exceptionHandler.handleValidationExceptions(ex);

        // 4. Asserções
        assertThat(response.getStatus()).isEqualTo(400);
        assertThat(response.getProperties()).containsKey("invalidFields");
    }
}