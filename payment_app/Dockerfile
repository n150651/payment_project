# 1. Use an official lightweight Python image
FROM python:3.12-slim

# 2. Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files
# PYTHONUNBUFFERED: Ensures logs are sent straight to the terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory
WORKDIR /app

# 4. Install system dependencies (needed for some Python DB drivers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements and install
# Note: Ensure 'gunicorn' is added to your requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application
COPY . .

# 7. Optimized Command for Real-Time Concurrency
# -w 4: Run 4 worker processes (Adjust based on CPU cores)
# -k uvicorn.workers.UvicornWorker: Use the high-speed async worker
# --bind: Listen on all interfaces
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000", "--timeout", "120"]