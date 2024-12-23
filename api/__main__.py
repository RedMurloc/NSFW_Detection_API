from api import predict, app
from api.functions import download_image
from config import PORT
from fastapi import Body
import base64
import os
import uvicorn

model = predict.load_model('nsfw_detector/nsfw_model.h5')


@app.get("/")
async def detect_nsfw(url: str):
    if not url:
        return {"ERROR": "URL PARAMETER EMPTY"}
    image = await download_image(url)
    if not image:
        return {"ERROR": "IMAGE SIZE TOO LARGE OR INCORRECT URL"}
    results = predict.classify(model, image)
    os.remove(image)
    hentai = results['data']['hentai']
    sexy = results['data']['sexy']
    porn = results['data']['porn']
    drawings = results['data']['drawings']
    neutral = results['data']['neutral']
    if neutral >= 25:
        results['data']['is_nsfw'] = False
        return results
    elif (sexy + porn + hentai) >= 70:
        results['data']['is_nsfw'] = True
        return results
    elif drawings >= 40:
        results['data']['is_nsfw'] = False
        return results
    else:
        results['data']['is_nsfw'] = False
        return results

@app.post("/")
async def detect_nsfw(data = Body()):
    imgdata = base64.b64decode(data["base64Image"])
    filename = 'image.jpg'
    with open(filename, 'wb') as f:
        f.write(imgdata)

    results = predict.classify(model, filename)
    os.remove(filename)

    hentai = results['data']['hentai']
    sexy = results['data']['sexy']
    porn = results['data']['porn']
    drawings = results['data']['drawings']
    neutral = results['data']['neutral']
    if (sexy + porn + hentai) >= 30:
        results['data']['is_nsfw'] = True
        return results 
    elif neutral >= 25:
        results['data']['is_nsfw'] = False
        return results
    elif drawings >= 40:
        results['data']['is_nsfw'] = False
        return results
    else:
        results['data']['is_nsfw'] = False
        return results

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=PORT, log_level="info")
