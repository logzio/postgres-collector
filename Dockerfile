FROM debian:stable-slim

# Use root account to use apt
USER root
# Install Python
RUN apt-get update -y && apt-get install python3 -y && apt-get install python3-pip -y && apt-get install curl -y
# Install dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --user && \
    rm -f requirements.txt

# Copy files
COPY config_files config_files
COPY queries queries
COPY testdata testdata
COPY builder.py builder.py
COPY config.py config.py
COPY input_validator.py input_validator.py

# Download opentelemetry binary
RUN curl -L https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.45.0/otelcol-contrib_0.45.0_linux_amd64.tar.gz -o otelcol-contrib.tar.gz
RUN tar -xf otelcol-contrib.tar.gz otelcol-contrib
RUN mv otelcol-contrib otelcontribcol_linux_amd64

# Download postgres_exporter binary
RUN curl -L https://github.com/percona/postgres_exporter/releases/download/v0.4.7/postgres_exporter_linux_amd64.tar.gz -o postgres_exporter.tar.gz
RUN tar -xf postgres_exporter.tar.gz

# Binary permmisions
RUN chmod +x otelcontribcol_linux_amd64
RUN chmod +x postgres_exporter
# Opentelemetry metrics
EXPOSE 8888
# Zpages
EXPOSE 55679
# Health check
EXPOSE 13133
# Pprof
EXPOSE 1777

EXPOSE 5001

EXPOSE 9187


CMD ["python3", "builder.py"]
