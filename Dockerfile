FROM registry.access.redhat.com/ubi8/ubi

# Install python3.9 and other necessary tools
# We use python39 because UBI8 default python3 is 3.6 which is quite old
RUN yum install -y python39 git zip && \
    yum clean all

# Set working directory
WORKDIR /app

# Create virtual environment
RUN python3.9 -m venv /app/venv

# Upgrade pip in venv
RUN /app/venv/bin/pip install --upgrade pip

# Copy requirements first to leverage cache
COPY requirements.txt .
RUN /app/venv/bin/pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure the script is executable
RUN chmod +x toolbox/cli.py

# Default command (can be overridden)
CMD ["/bin/bash"]
