FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml LICENSE README.md /app/
COPY src/ /app/src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

EXPOSE 9999

CMD ["elasticsearch7-mcp-server"] 