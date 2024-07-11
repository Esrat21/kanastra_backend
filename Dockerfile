FROM jupyter/all-spark-notebook:latest

USER root

# Atualizar e instalar dependências necessárias
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.9 python3.9-dev python3.9-distutils python3-pip openjdk-11-jdk wget build-essential libssl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Atualizar pip para a versão mais recente
RUN python3.9 -m pip install --upgrade pip

# Baixar e instalar Apache Spark 3.5.1 com Hadoop 3
RUN wget -O /tmp/spark-3.5.1-bin-hadoop3.tgz https://dlcdn.apache.org/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz && \
    tar -xz -C /opt/ -f /tmp/spark-3.5.1-bin-hadoop3.tgz && \
    mv /opt/spark-3.5.1-bin-hadoop3 /opt/spark && \
    rm /tmp/spark-3.5.1-bin-hadoop3.tgz

# Definir variáveis de ambiente
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$JAVA_HOME/bin:$PATH

USER jovyan

# Configurar o diretório de trabalho
WORKDIR /home/jovyan/app

# Copiar o código do projeto e os requisitos
COPY . .

# Instalar dependências do projeto usando python3.9
RUN python3.9 -m pip install --no-cache-dir -r requirements.txt

# Adicionar o diretório de scripts do Python ao PATH
ENV PATH="/home/jovyan/.local/bin:${PATH}"

# Comando para iniciar o servidor FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
