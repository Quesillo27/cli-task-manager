FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /root/.task-manager

# Install in editable mode
RUN pip install -e .

ENTRYPOINT ["task"]
CMD ["--help"]
