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
COPY cw_namespaces cw_namespaces
COPY testdata testdata
COPY builder.py builder.py
COPY config.py config.py
COPY input_validator.py input_validator.py

# Download opentelemetry binary
COPY otelcontribcol_linux_amd64 otelcontribcol_linux_amd64
COPY postgres_exporter postgres_exporter
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
