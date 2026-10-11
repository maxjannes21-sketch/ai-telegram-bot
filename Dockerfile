FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
# Сначала torch в CPU-версии: без этого он тянет CUDA-библиотеки на 2+ ГБ,
# которые нам на сервере без видеокарты не нужны
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]