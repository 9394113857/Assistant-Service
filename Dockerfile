# 1. Use lightweight Python image
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy dependency file first (for caching)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy project files
COPY . .

# 6. Apply database migrations before starting the web server.
# If migration fails, the container fails closed instead of serving
# requests against an outdated schema.
# 7. Run the app with Gunicorn.
CMD ["sh", "-c", "flask --app run:app db upgrade && exec gunicorn run:app -w 1 -b 0.0.0.0:$PORT --access-logfile - --error-logfile -"]
