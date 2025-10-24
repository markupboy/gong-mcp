FROM python:3.11-slim

WORKDIR /app

# Copy dependency files
COPY requirements.txt pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir -e .

# Start the server
CMD ["python", "-m", "gong_mcp.server"] 