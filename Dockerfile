# Use a lightweight python image
FROM python:3.11-slim

# Install system dependencies (LaTeX compiler and fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    && rm -rf /var/lib/apt/lists/*

# Set up a working directory
WORKDIR /code

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy all code
COPY . .

# Hugging Face Spaces run on port 7860 by default for Docker SDK
EXPOSE 7860

# Run Streamlit on port 7860 and bind to 0.0.0.0
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
