PYTHON_3_8_DOCKERFILE_TEMPLATE = """FROM python:3.8
COPY ./ /tmp/
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt
RUN useradd -u 9097 code_runner
USER code_runner:code_runner
WORKDIR /tmp
CMD ["bash", "-c", "python main.py > /tmp/logs/execution.log 2>&1"]
"""

PYTHON_3_9_DOCKERFILE_TEMPLATE = """FROM python:3.9
COPY ./ /tmp/
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt
RUN useradd -u 9097 code_runner
USER code_runner:code_runner
WORKDIR /tmp
CMD ["bash", "-c", "python main.py > /tmp/logs/execution.log 2>&1"]
"""

PYTHON_3_10_DOCKERFILE_TEMPLATE = """FROM python:3.10
COPY ./ /tmp/
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt
RUN useradd -u 9097 code_runner
USER code_runner:code_runner
WORKDIR /tmp
CMD ["bash", "-c", "python main.py > /tmp/logs/execution.log 2>&1"]
"""

PYTHON_3_11_DOCKERFILE_TEMPLATE = """FROM python:3.11
COPY ./ /tmp/
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt
RUN useradd -u 9097 code_runner
USER code_runner:code_runner
WORKDIR /tmp
CMD ["bash", "-c", "python main.py > /tmp/logs/execution.log 2>&1"]
"""

PYTHON_3_12_DOCKERFILE_TEMPLATE = """FROM python:3.12
COPY ./ /tmp/
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt
RUN useradd -u 9097 code_runner
USER code_runner:code_runner
WORKDIR /tmp
CMD ["bash", "-c", "python main.py > /tmp/logs/execution.log 2>&1"]
"""

NODE_24_DOCKERFILE_TEMPLATE = """FROM node:24
COPY ./ /tmp/
WORKDIR /tmp
RUN npm install --production --loglevel verbose
RUN useradd -u 9097 code_runner
USER code_runner:code_runner
CMD ["bash", "-c", "node main.js > /tmp/logs/execution.log 2>&1"]
"""

R_4_5_DOCKERFILE_TEMPLATE = """FROM r-base:4.5.0
COPY ./ /tmp/
WORKDIR /tmp
RUN apt-get update && apt-get install -y \
    libgmp-dev libcurl4-openssl-dev libssl-dev libxml2-dev \
    && rm -rf /var/lib/apt/lists/*
RUN Rscript -e "install.packages('renv', repos='https://cran.rstudio.com/')"
RUN mkdir -p /tmp/renv/.cache
ENV RENV_PATHS_CACHE=/tmp/renv/.cache
RUN Rscript -e "tryCatch(renv::restore(prompt = FALSE), error = function(e) { message('Package installation failed: ', e); quit(status = 1) })"
RUN useradd -u 9097 -m code_runner
ENV HOME=/home/code_runner
USER code_runner:code_runner
CMD ["bash", "-c", "Rscript main.R > /tmp/logs/execution.log 2>&1"]
"""