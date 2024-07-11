import logging
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .modelos import Divida
from .servicos import processar_csv, gerar_boleto_sync, enviar_email_sync, calcular_hash, get_processed_boletos
from .database import get_db

app = FastAPI()

# Configurar logging para arquivo
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adicionar um manipulador de arquivo para salvar logs em um arquivo
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levellevel)s - %(message)s'))
logger.addHandler(file_handler)

# Endpoint para upload de arquivos CSV.
# Processa o arquivo CSV, gera boletos e envia e-mails simulados.
@app.post("/uploadfile/")
async def criar_arquivo_upload(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        logger.error("Formato de arquivo inválido. Apenas arquivos CSV são aceitos.")
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Apenas arquivos CSV são aceitos.")
    
    try:
        boletos_existentes = get_processed_boletos(db)
        dividas, novos_boletos = await asyncio.wait_for(processar_csv(file, boletos_existentes), timeout=60)
        for divida in dividas:
            boleto_hash = calcular_hash(divida)
            if boleto_hash in boletos_existentes:
                logger.info(f"Boleto já processado para o documento {divida.documento}. Ignorando duplicado.")
                continue
            boletos_existentes.add(boleto_hash)
            background_tasks.add_task(gerar_boleto_sync, db, divida, boletos_existentes)
            background_tasks.add_task(enviar_email_sync, db, divida.email, divida)
        logger.info("Arquivo processado com sucesso.")
        return JSONResponse(status_code=200, content={"mensagem": "Arquivo processado com sucesso, emails serão enviados em background"})
    except asyncio.TimeoutError:
        logger.warning("O processamento do arquivo demorou mais de 60 segundos. O processamento continuará em segundo plano.")
        background_tasks.add_task(processar_csv, file, boletos_existentes)
        return JSONResponse(status_code=200, content={"mensagem": "O processamento do arquivo demorou mais de 60 segundos. O processamento continuará em segundo plano."})
    except Exception as e:
        logger.error(f"Erro ao processar o arquivo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
