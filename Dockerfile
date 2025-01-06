FROM continuumio/miniconda3:latest

WORKDIR /app

# Copy environment file
COPY environment.yml .

# Create conda environment
RUN conda env create -f environment.yml

# Copy application code
COPY . .

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "bubble-beaver", "/bin/bash", "-c"]

# Create data directory for prompts
RUN mkdir -p data

# Command to run the bot
CMD ["conda", "run", "-n", "bubble-beaver", "python", "main.py"]
