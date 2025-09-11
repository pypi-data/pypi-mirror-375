FROM python:3.11-bullseye

COPY dist/*.whl /tmp/source/

RUN cd /tmp/source && \
    python3 -m pip install /tmp/source/*.whl
