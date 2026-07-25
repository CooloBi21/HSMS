FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system hsms && adduser --system --ingroup hsms hsms

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN sed -i 's/\r$//' /app/docker/*.sh \
    && chmod +x /app/docker/entrypoint.sh \
    && chown -R hsms:hsms /app

USER hsms

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "run:app", "-c", "gunicorn.conf.py"]
