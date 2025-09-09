FROM python:3.12

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install vearne-akshare-mcp -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["/usr/local/bin/python3", "-m", "vearne_akshare_mcp", "--http", "--bind=0.0.0.0", "--port=8090"]
