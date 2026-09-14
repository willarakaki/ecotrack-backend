# Estágio 1: Build (Imutável)
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app
# Copia o wrapper e arquivos do maven primeiro para cache de dependências
COPY .mvn/ .mvn/
COPY mvnw pom.xml ./
RUN ./mvnw dependency:go-offline -B

# Copia o código-fonte e compila
COPY src ./src
RUN ./mvnw clean package -DskipTests

# Estágio 2: Runtime (Segurança: Imagem leve, sem ferramentas de build)
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /app/target/core-0.0.1-SNAPSHOT.jar ./ecotrack-core.jar

# Exposição da porta configurada no application.yml
EXPOSE 8080

# Entrypoint executando a aplicação
ENTRYPOINT ["java", "-jar", "ecotrack-core.jar"]