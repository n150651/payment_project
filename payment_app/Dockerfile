# 1. Use an official lightweight Python image
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file first (for caching layers)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Command to run the application
# host 0.0.0.0 is crucial for Docker networking!
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
