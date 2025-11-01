# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies for pygame
RUN apt-get update && apt-get install -y \
    libsdl2-2.0 \
    libsdl2-image-2.0 \
    libsdl2-mixer-2.0 \
    libsdl2-ttf-2.0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy game file
COPY snake_game.py .

# Copy music files (optional - game works without them)
COPY "Now It Rains.mp3"* ./
COPY "Dreamin'.mp3"* ./

# Run the game
CMD ["python", "snake_game.py"]
