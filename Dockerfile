FROM python:3.9-slim-buster
WORKDIR /greeting-cards
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . /greeting-cards
CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "-p", "5000"]
