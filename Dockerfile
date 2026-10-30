FROM python:3.13-slim
WORKDIR /greeting-cards
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . /greeting-cards
# .flaskenv is excluded from the image (it enables the debugger), so set the app here instead.
# Override FLASK_DEBUG in the stack's environment only when debugging.
ENV FLASK_APP=main.py FLASK_DEBUG=0
CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "-p", "5000"]
