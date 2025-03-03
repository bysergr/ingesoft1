FROM python:3.10

WORKDIR /code

COPY ./src /code/src
COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["python3", "-m", "src.main"]
