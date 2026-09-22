package com.ecotrack.core.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.net.URI;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public ProblemDetail handleBusinessException(BusinessException ex) {
        log.warn("Violação de regra de negócio: {}", ex.getMessage());

        // Uso da interface HttpStatusCode via valueOf para evitar depreciação
        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(org.springframework.http.HttpStatusCode.valueOf(422), ex.getMessage());
        problemDetail.setTitle("Violação de Regra de Negócio");
        problemDetail.setType(URI.create("https://ecotrack.com/api/errors/business-rule"));
        problemDetail.setProperty("timestamp", Instant.now());

        return problemDetail;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidationExceptions(MethodArgumentNotValidException ex) {
        log.warn("Falha de validação de payload detectada (Edge Security)");

        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(org.springframework.http.HttpStatusCode.valueOf(400), "A requisição contém parâmetros inválidos ou mal formatados.");
        problemDetail.setTitle("Erro de Validação (Bad Request)");
        problemDetail.setType(URI.create("https://ecotrack.com/api/errors/validation"));
        problemDetail.setProperty("timestamp", Instant.now());

        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach(error -> {
            String fieldName = ((FieldError) error).getField();
            String errorMessage = error.getDefaultMessage();
            errors.put(fieldName, errorMessage);
        });

        problemDetail.setProperty("invalidFields", errors);

        return problemDetail;
    }

    @ExceptionHandler(IllegalStateException.class)
    public ProblemDetail handleIllegalStateException(IllegalStateException ex) {
        log.warn("Operação ilegal interceptada: {}", ex.getMessage());

        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, ex.getMessage());
        problemDetail.setTitle("Operação Não Permitida");
        problemDetail.setType(URI.create("https://ecotrack.com/api/errors/illegal-state"));
        problemDetail.setProperty("timestamp", Instant.now());
        return problemDetail;
    }

    @ExceptionHandler(org.springframework.dao.OptimisticLockingFailureException.class)
    public ProblemDetail handleConcurrencyException(org.springframework.dao.OptimisticLockingFailureException ex) {
        log.warn("Colisão de concorrência detectada (Double Spending attempt bloqueada).");

        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, "A solicitação colidiu com outra operação em andamento. Por favor, atualize seus dados e tente novamente.");
        problemDetail.setTitle("Conflito de Concorrência");
        problemDetail.setType(URI.create("https://ecotrack.com/api/errors/conflict"));
        problemDetail.setProperty("timestamp", Instant.now());
        return problemDetail;
    }

    @ExceptionHandler(Exception.class)
    public ProblemDetail handleAllUncaughtException(Exception ex) {
        // Logamos o erro verdadeiro para o Sentry/Datadog, mas NUNCA expomos ao cliente (OWASP)
        log.error("Erro interno catastrófico não mapeado: ", ex);

        ProblemDetail problemDetail = ProblemDetail.forStatusAndDetail(HttpStatus.INTERNAL_SERVER_ERROR, "Ocorreu um erro interno no servidor. Nossa equipe de engenharia já foi notificada.");
        problemDetail.setTitle("Erro Interno de Servidor");
        problemDetail.setType(URI.create("https://ecotrack.com/api/errors/internal-server-error"));
        problemDetail.setProperty("timestamp", Instant.now());

        return problemDetail;
    }
}