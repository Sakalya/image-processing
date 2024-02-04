from fastapi import FastAPI, Header, Security, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
import csv
import uuid
from services import image_service, database_service

# Some standard logger formatting and customization
# create logger
logger = logging.getLogger('images')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

app = FastAPI()
# Reading some parameter constant, from the .env file
# COLUMNS_NR: this can fix the required amount of pixel to be uploaded in the CSV file
# AUTH_TOKEN: Auth token/password to be sure the request is authenticated
COLUMNS_NR = int(os.getenv('COLUMNS_NR', 200))
AUTH_TOKEN = os.getenv('AUTH_TOKEN', '123')

# This is a sample way to make any endpoint secure.
# In this function, it would be possible to call an external service to authenticate in the preferred way.
# For now it is only checking if the user is passing the token/password and that maateches what's in the env file.
async def get_token(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    if authorization != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Permission denied. Wrong token")
    return authorization

# An endpoint to get a single image as StreamingResponse png object
@app.get("/image/")
def get_image(depth: int):
    try:
        db = database_service.DbManager()
        img_proc = image_service.ImageProcessor()
        # Retrieve and return a single image from the DB
        image = db.get_image(depth)

        if not image or len(image) == 0:
            raise Exception("Depth not available")
        
        image_buffer = img_proc.decode_image(image)

        return StreamingResponse(image_buffer, media_type="image/png")
    except Exception as e:
        # The error log should be also handled and sent somewhere, to better run any analysis
        logger.error(e)
        return f"Internal Error occurred. {e}"


# This endpoint expects a GET request, with 2 mandatory parameters: depth_min and depth_max
# The range of base64 encord images will be then fetched on the DB and sent back as an array.
# The assumption is that the client will then be able to decode those images on its side.
@app.get("/images")
def get_images(depth_min: int, depth_max: int):
    try:
        db = database_service.DbManager()

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
        # The error log should be also handled and sent somewhere, to better run any analysis
        logger.error(e)
        return f"Internal Error occurred."


# Simple implementation of a protected POST request, where it is possible to upload a new CSV, in the accepted format.
# If any line is in the invalid format, the invalid_rows will be populated with it.
# The DB will replace any image at any depth if already present in the table, using the depth key.
# Note: for simplicity, there are no many sanity checks here.
@app.post("/add")
async def add_images(csv_file: UploadFile = File(...), token: str = Security(get_token)):
    try:
        # Read the contents of the uploaded file
        contents = await csv_file.read()

        # Decode the contents to a string and split into lines
        decoded_contents = contents.decode('utf-8').splitlines()
        # Process the CSV data
        csv_reader = csv.reader(decoded_contents)
        data = [row for row in csv_reader]

        # Write the CSV data to the file
        random_file_name = f"{uuid.uuid4()}.csv"
        print(random_file_name)
        with open(random_file_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(data)

        images, invalid_lines = read_images_from_csv(random_file_name)

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
        # The error log should be also handled and sent somewhere, to better run any analysis
        logger.error(e)
        return f"Internal Error occurred."


# A default endpoint, where a documentation of the API could be presented
@app.get("/")
def hellow_world():
    return 'API welcome endpoint'

# This function is responsible of loading the data into the DB, from the CSV. 
# It will also:
# - Check if each line is valid (correct number of non-empty fields, with pixel values between 0 and 255)
# - Return a dcistionary with depth->image_data structure
def read_images_from_csv(csv_file):
    images = {}
    invalid_lines = []

    # Read CSV
    with open(csv_file, 'r') as file:
        for index, line in enumerate(file):
            # Strip newline characters and other surrounding whitespace
            line = line.strip()
            # Split the line into fields
            line = line.split(',')

            # Skipping the headers
            if index > 0 and is_line_valid(line=line):
                # The first column contains the depth abd the hehigh pixel for that image
                depth, height = map(int, line[0].split('.'))
                # Image data is in the rest of the column
                image_data = line[1:]

                if depth not in images:
                    images[depth] = []
                images[depth].append(image_data)
            else:
                if index != 0: # Skip the header
                    logger.warning(f'Invalid Line at index {index}')
                    invalid_lines.append(index)

    logger.info("New daa loaded in the DB")
    return images, invalid_lines


# Multiple sanity checks
def is_line_valid(line):
    # Invalid line already if it has less or more elements
    # Correct number is the image width + 1 as depth reference
    if len(line) != COLUMNS_NR + 1:
        return False
    
    for index, value in enumerate(line):
        # skip the first column or we do a separate check for it
        if index == 0:
            continue
        if value is not None and value != '':
            if int(value) >= 0 and int(value) <= 255:
                continue
        # If it didn't pass any check, at least one value is wrong
        return False
    return True


# This is the application starting point.
# - It calls the DB (which will initiate)
# - It loads the default CSV
# - It structures, reshapes and b64 encode the images
# - It stores them in the DB
# - It spins up the HTTP server
if __name__ == "__main__":
    logger.info(f"Number of columns: {COLUMNS_NR}")

    try:
        db = database_service.DbManager()
        img_proc = image_service.ImageProcessor()
        # Read rows from the CSV and sends a warning about the invalid lines
        images, invalid_lines = read_images_from_csv('/app/img.csv')
        logger.info(f'Images found: {len(images)}')
        logger.warning(f'Invalid images found: {len(invalid_lines)}')
        images = img_proc.load_and_resize_images(images=images)

        # Insert array of images in the DB
        db.insert_images(images)
        logger.info("Initial data created")
        
        # Run the API
        uvicorn.run(app, host="0.0.0.0", port=8000)

    except Exception as e:
        logger.error(e)
        # The error log should be also handled and sent somewhere, to better run any analysis
        exit(1)