#syntax=docker/dockerfile:1

FROM sphinxdoc/sphinx-latexpdf
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

ENTRYPOINT ["python3", "pycook.py"]

