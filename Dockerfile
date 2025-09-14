
FROM ubuntu:22.04

# 支援 build-time 與 run-time 指定 wkhtmltopdf 路徑
ARG WKHTMLTOPDF_PATH=/usr/local/bin/wkhtmltopdf
ENV WKHTMLTOPDF_PATH=${WKHTMLTOPDF_PATH}

ENV DEBIAN_FRONTEND=noninteractive

# --- 安裝系統工具與相依 ---
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    ca-certificates wget curl gnupg2 lsb-release software-properties-common \
    build-essential dpkg fontconfig libxrender1 libxext6 libx11-6 libxcb1 libfreetype6 libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# --- 安裝 Python 3.12 (deadsnakes) 與 pip ---
RUN set -eux; \
    add-apt-repository ppa:deadsnakes/ppa -y; \
    apt-get update; \
    apt-get install -y --no-install-recommends python3.12 python3.12-venv python3.12-dev python3-distutils; \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12 -; \
    python3.12 -m pip install --upgrade pip setuptools wheel; \
    rm -rf /var/lib/apt/lists/*

# --- 安裝 wkhtmltopdf（COPY 方式） ---
# 請先把 wkhtmltox_0.12.6-1.jammy_amd64.deb 放到專案根目錄，再執行 docker build
COPY wkhtmltox_0.12.6-1.jammy_amd64.deb /tmp/wkhtml.deb
RUN set -eux; \
    apt-get update; \
    dpkg -i /tmp/wkhtml.deb || (apt-get -f install -y && dpkg -i /tmp/wkhtml.deb); \
    rm -f /tmp/wkhtml.deb; \
    # 若 wkhtmltopdf 安裝到不同位置，嘗試建立到 WKHTMLTOPDF_PATH 的符號連結，方便程式預設使用
    mkdir -p "$(dirname ${WKHTMLTOPDF_PATH})"; \
    for p in /usr/local/bin/wkhtmltopdf /usr/bin/wkhtmltopdf /opt/wkhtmltopdf/bin/wkhtmltopdf; do \
        if [ -x "$p" ]; then \
            ln -sf "$p" "${WKHTMLTOPDF_PATH}" || true; \
            echo "Linked $p -> ${WKHTMLTOPDF_PATH}"; \
            break; \
        fi; \
    done; \
    rm -rf /var/lib/apt/lists/*

# --- 複製專案並安裝 Python 相依 ---
WORKDIR /app
COPY . /app

RUN python3.12 -m pip install --no-cache-dir -r requirements.txt

# --- entrypoint ---
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["full"]

