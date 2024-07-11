import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_uploadfile_invalid_format():
    response = client.post("/uploadfile/", files={"file": ("test.txt", "some content")})
    assert response.status_code == 400
    assert response.json() == {"detail": "Formato de arquivo inválido. Apenas arquivos CSV são aceitos."}

@pytest.mark.asyncio
async def test_uploadfile_valid_format():
    csv_content = """name,governmentId,email,debtAmount,debtDueDate,debtId
John Doe,12345678901,john.doe@example.com,1000.0,2023-12-31,1a2b3c4d5e
Jane Doe,09876543210,jane.doe@example.com,500.0,2023-11-30,6f7g8h9i0j"""
    
    response = client.post("/uploadfile/", files={"file": ("input.csv", csv_content)})
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Arquivo processado com sucesso, emails serão enviados em background"}
