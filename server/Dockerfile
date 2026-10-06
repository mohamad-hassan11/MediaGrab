FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    unzip \
    git \
    ca-certificates \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# PO Token provider: a local HTTP server that generates YouTube
# proof-of-origin tokens, used by the bgutil-ytdlp-pot-provider yt-dlp
# plugin to avoid "Sign in to confirm you're not a bot" errors without
# needing any logged-in cookies.
# https://github.com/Brainicism/bgutil-ytdlp-pot-provider
ARG BGUTIL_POT_VERSION=2.0.1
RUN git clone --depth 1 --branch ${BGUTIL_POT_VERSION} \
    https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git \
    /opt/bgutil-ytdlp-pot-provider \
    && cd /opt/bgutil-ytdlp-pot-provider/server \
    && npm ci \
    && npx tsc

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY entrypoint.sh .

RUN mkdir -p /app/temp \
    && chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]