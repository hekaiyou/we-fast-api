FROM python:3.10.11
WORKDIR /workspace
COPY . /workspace/
RUN pip install -r requirements.txt
# Build serve - Start
# For example: RUN pip install -r apis/demo_serve/requirements.txt
# Build serve - End
EXPOSE 8083
CMD ["python", "main.py"]