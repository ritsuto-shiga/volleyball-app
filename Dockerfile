# Use an official lightweight Python image.
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . /app

# Streamlit config for container
ENV STREAMLIT_SERVER_PORT=8080 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLECORS=false

EXPOSE 8080

CMD ["streamlit", "run", "volley_app.py", "--server.port=8080", "--server.address=0.0.0.0"]
