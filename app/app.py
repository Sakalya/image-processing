from fastapi import FastAPI, Header, Security, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
import os
import logging
import csv
import uuid

from util import validation
from services import image_processing_service, image_db_service

# Initialize logger with standard formatting
logger = logging.getLogger('images')
logger.setLevel(logging.INFO)
app = FastAPI()

# Read environment variables
AUTH_TOKEN = os.getenv('AUTH_TOKEN', 'test')

async def get_token(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    if authorization != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Permission denied. Wrong token")
    return authorization


@app.get("/image/")
def get_image(depth: int):
    try:
        db = image_db_service.DbManager()
        image_processor = image_processing_service.ImageProcessor()
        image = db.get_image(depth)

        if not image or len(image) == 0:
            raise Exception("Depth not available")

        image_buffer = image_processor.decode_image(image)
        return StreamingResponse(image_buffer, media_type="image/png")
    except Exception as e:
        logger.error(e)
        return f"Internal Error occurred. {e}"


@app.get("/images")
def get_images(depth_min: int, depth_max: int):
    try:
        db = image_db_service.DbManager()
        images = db.get_images(depth_min, depth_max)

        if len(images) == 0:
            raise HTTPException(status_code=500, detail="No images found at the depths provided")

        response = {
            'images_data': images,
            'depth_min': depth_min,
            'depth_max': depth_max
        }
        return JSONResponse(content=response)
    except HTTPException as e:
        logger.error(e)
        return e
    except Exception as e:
        logger.error(e)
        return f"Internal Error occurred."

    # Add images from CSV
    @app.post("/add")
    async def add_images(csv_file: UploadFile = File(...), token: str = Security(get_token)):
        try:
            contents = await csv_file.read()
            decoded_contents = contents.decode('utf-8').splitlines()
            csv_reader = csv.reader(decoded_contents)
            data = [row for row in csv_reader]

            random_file_name = f"{uuid.uuid4()}.csv"
            with open(random_file_name, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(data)

            images, invalid_lines = image_processor.read_images_from_csv(random_file_name, validator)

            response = {
                'status': 'Ok',
                'loaded_images': len(images),
                'invalid_rows': invalid_lines
            }
            return JSONResponse(content=response)
        except HTTPException as e:
            logger.error(e)
            return e
        except Exception as e:
            logger.error(e)
            return f"Internal Error occurred."


# Application startup point
if __name__ == "__main__":
    try:
        db = image_db_service.DbManager()
        validator = validation.Validator()
        image_processor = image_processing_service.ImageProcessor()
        images, invalid_lines = image_processor.read_images_from_csv('/app/img.csv', validator)
        logger.warning(f'Invalid images found: {len(invalid_lines)}')
        images = image_processor.load_and_resize_images(images=images)

        db.insert_images(images)
        logger.info("Initial data created")

        uvicorn.run(app, host="0.0.0.0", port=8000)

    except Exception as e:
        logger.error(e)
        exit(1)
