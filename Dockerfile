FROM ubuntu

RUN apt update && apt install python3 python3-pip curl -y

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY entrypoint.sh /entrypoint.sh
COPY sync_upstream /sync_upstream
COPY pyproject.toml /pyproject.toml
COPY config.example.yaml /config.example.yaml

# Install dependencies with uv
RUN /root/.cargo/bin/uv pip install -e .

ENTRYPOINT ["/entrypoint.sh"]
