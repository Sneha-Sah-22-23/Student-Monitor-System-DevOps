FROM apache/spark:3.5.0

USER 0

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip install --no-cache-dir flask plotly pandas pyarrow pyspark

WORKDIR /app

COPY analysis.py .
COPY dashboard.py .

VOLUME ["/app/data"]

EXPOSE 5000

CMD ["python3", "dashboard.py"]

