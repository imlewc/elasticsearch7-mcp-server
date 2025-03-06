FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml /app/
COPY src/ /app/src/

RUN pip install --no-cache-dir -e .

EXPOSE 9999

CMD ["elasticsearch7-mcp-server"] 