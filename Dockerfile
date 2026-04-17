FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /root/.task-manager \
    && pip install --no-cache-dir -e .

# CLI healthcheck — confirms the entry point is installed and executable.
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD task version || exit 1

ENTRYPOINT ["task"]
CMD ["--help"]
