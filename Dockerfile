FROM python:3.12.3

WORKDIR /app
COPY joan_miro.py /app
COPY requirements.txt /app

RUN pip install -r requirements.txt
RUN mkdir -p /app/images


CMD ["python", "joan_miro.py"]