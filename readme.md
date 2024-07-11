
# Sistema de Processamento de Boletos

## Sumário
- [Sobre](#sobre)
- [Configuração](#configuração)
- [Execução](#execução)
- [Testes](#testes)
- [Estrutura do CSV](#estrutura-do-csv)
- [Instruções de Envio do CSV](#instruções-de-envio-do-csv)

## Sobre
Este projeto implementa um sistema de processamento de boletos que inclui:
- Upload de arquivos CSV.
- Processamento de registros de forma performática.
- Geração de boletos e envio de e-mails simulados.
- Controle rigoroso para evitar duplicidades.
- Tratamento de erros robusto e logging detalhado.

## Configuração
1. **Clone o repositório**:
   ```bash
   git clone https://github.com/Esrat21/kanastra_backend
   cd kanastra_backend
   ```

2. **Crie o arquivo `requirements.txt`** com o seguinte conteúdo:
   ```plaintext
   fastapi
   uvicorn
   sqlalchemy
   pytest
   pytest-asyncio
   httpx
   ```

3. **Crie o arquivo `docker-compose.yml`** com o seguinte conteúdo:
   ```yaml
   services:
     app:
       build:
         context: .
       volumes:
         - .:/home/jovyan/app
       ports:
         - "8000:8000"
       environment:
         JAVA_HOME: /usr/lib/jvm/java-11-openjdk-amd64
         SPARK_HOME: /opt/spark
       command: ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]
   ```

4. **Crie o arquivo `Dockerfile`** com o seguinte conteúdo:
   ```dockerfile
   FROM jupyter/all-spark-notebook:latest

   USER root

   # Instalar dependências necessárias, incluindo o Java
   RUN apt-get update &&        apt-get install -y python3-pip openjdk-11-jdk &&        apt-get clean

   # Definir JAVA_HOME corretamente
   ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
   ENV PATH=$JAVA_HOME/bin:$PATH

   USER jovyan

   # Configurar o diretório de trabalho
   WORKDIR /home/jovyan/app

   # Copiar o código do projeto e os testes
   COPY . .

   # Instalar dependências do projeto e uvicorn
   RUN pip install --no-cache-dir -r requirements.txt uvicorn

   # Adicionar o diretório de scripts do Python ao PATH
   ENV PATH="/home/jovyan/.local/bin:${PATH}"

   # Comando para iniciar o servidor FastAPI
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

## Execução
1. **Build do Docker**:
   ```bash
   docker-compose build
   ```

2. **Iniciar o contêiner**:
   ```bash
   docker-compose up
   ```

3. **A API estará disponível em**: `http://localhost:8000`

## Testes
Para rodar os testes unitários e de integração, utilize:
```bash
pytest --tb=short -q
```

## Estrutura do CSV
O arquivo CSV deve conter as seguintes colunas:
1. **name** → nome
2. **governmentId** → número do documento
3. **email** → email do sacado
4. **debtAmount** → valor
5. **debtDueDate** → Data para ser paga
6. **debtID** → uuid para o débito

## Instruções de Envio do CSV
### Usando o Insomnia
1. Abra o Insomnia e crie uma nova requisição.
2. Configure a requisição como `POST`.
3. No campo URL, insira `http://localhost:8000/uploadfile/`.
4. Vá para a aba `Body` e selecione `Form Data`.
5. Adicione um campo com o nome `file` e, no campo de valor, selecione o arquivo CSV que deseja enviar.
6. Clique em `Send` para enviar a requisição.

### Usando o cURL
```bash
curl -X POST "http://localhost:8000/uploadfile/" -F "file=@path/to/your/input.csv"
```

### Usando o Python Requests
```python
import requests

url = "http://localhost:8000/uploadfile/"
file_path = "path/to/your/input.csv"

with open(file_path, "rb") as f:
    response = requests.post(url, files={"file": f})

print(response.json())
```
