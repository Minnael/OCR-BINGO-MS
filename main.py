from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
import re

app = FastAPI(title="Bingo OCR Microservice")

# ✅ Habilitar CORS
origins = ["*"]  # permite qualquer origem; ou coloque apenas seu domínio frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],    
)

@app.get("/")
def root():
    return {"message": "Serviço OCR ativo!"}

@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    try:
        # Ler imagem enviada
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # OCR usando Tesseract
        text = pytesseract.image_to_string(image, lang='eng+por')

        # Extrair números do texto
        tokens = re.findall(r'\d+', text)
        numeros_detectados = []
        seen = set()
        for t in tokens:
            n = int(t)
            if n < 100 and n not in seen:
                seen.add(n)
                numeros_detectados.append(n)

        return JSONResponse({
            "texto_extraido": text,
            "numeros_detectados": numeros_detectados
        })
    except Exception as e:
        return JSONResponse({"erro": str(e)}, status_code=500)
