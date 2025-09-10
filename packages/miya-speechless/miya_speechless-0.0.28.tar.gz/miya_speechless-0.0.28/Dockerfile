# Use the official Ubuntu base image with Python 3.12
FROM ubuntu:22.04

# Set environment variables to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install prerequisites for adding PPAs and other dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Add the deadsnakes PPA for Python 3.12
RUN add-apt-repository ppa:deadsnakes/ppa

# Update the package list to include packages from the new PPA
RUN apt-get update

# Install Python 3.12 and necessary development packages
RUN apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.12
RUN wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py && \
    python3.12 get-pip.py && \
    rm get-pip.py

# Create a symbolic link for python3 to point to python3.12
RUN ln -s /usr/bin/python3.12 /usr/local/bin/python3

# Upgrade pip to the latest version
RUN python3 -m pip install --upgrade pip

# Install the CPU version of PyTorch (without CUDA support)
RUN pip install torch torchvision torchaudio

# Install required Python packages
RUN pip install \
    transformers \
    pydub \
    pyannote.audio \
    jupyterlab \
    pytubefix \
    python-dotenv \
    openai

# Set the working directory
WORKDIR /app

# Expose Jupyter port
EXPOSE 8888

# Set environment variable for Jupyter to listen on all interfaces
ENV JUPYTER_ENABLE_LAB=yes

# Set the default command to launch Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
