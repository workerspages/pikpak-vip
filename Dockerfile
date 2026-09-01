FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY werbio_v1.2.py .
# 注意：不 COPY emails.txt，留到运行时挂载
EXPOSE 8081
CMD ["python", "-u", "werbio_v1.2.py"]
