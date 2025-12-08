FROM python:3.13-slim
WORKDIR /greeting-cards
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . /greeting-cards
CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "-p", "5000"]
