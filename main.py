from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
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

         # ===== Pré-processamento =====
        image = image.convert("L")  # grayscale
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)  # aumentar contraste
        image = image.filter(ImageFilter.MedianFilter(size=3))  # reduzir ruído
        image = image.point(lambda x: 0 if x < 128 else 255, '1')  # binarização opcional
        
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
