FROM python:3.12-slim

WORKDIR /Herasymenko

RUN pip install --no-cache-dir googletrans==3.1.0a0

COPY translation_pkg ./translation_pkg
COPY gtrans3.py ./gtrans3.py

CMD ["python", "gtrans3.py"]
