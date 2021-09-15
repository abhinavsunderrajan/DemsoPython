from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from io import BytesIO
import torch
import uvicorn
from PIL import Image
import base64
import sys
import json

model = torch.hub.load('yolov5', 'custom', path="model/best.pt",
                       source='local')
print("loaded pool detect model")
app = FastAPI()


class Data(BaseModel):
    im_b64: str


@app.post("/detect")
async def detect(data: Data):
    obj = {}
    try:
        print("recieve bytes data")
        im_bytes = base64.b64decode(data.im_b64)
        im_file = BytesIO(im_bytes)
        image = Image.open(im_file)
        print("decoded bytes data")
        result = model(image)
        json_string = result.pandas().xyxy[0].to_json(orient="records")
        obj = json.loads(json_string)
        print("send results back")
    except Exception:
        e = sys.exc_info()[1]
        raise HTTPException(status_code=400, detail=str(e))

    return obj

# for local testing
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
