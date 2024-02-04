# Simple Python Image processing app

This is a simple FastAPI application, which allows few simple operations:

1) Upload a new CSV file, which will make the app replacing or add the provided images within this file, in the main DB;
2) Get a single image frame, at a specific depth;
3) Get a series of image frames, at a specific depth range.

**Notes**: 
- The chosen DB is the `SQLite 3` for simplicity of this exercise. It will be completeley regenerated on each run, unless the application runs on a specific exernal mount. The module/class responsible for the DB interaction could be easily swapped with another technology/DB, keeping the same interface.
- The Security level which protects the POST call is basic, it only consists of a secret token/password to send along, within the *Authorization header*.
- Images can be of any height (using the counter, along with the depth), but to change the number of allowed columns the .env file needs to be updated accordingly.
- Images are resized using a ratio for the height, to get to the 150px width.
- Few libraries have been used, for simplicity reasons: PIL (Python Image Library - Pillow), csv, FastAPI and uvicorn, python-multipart.
- Still for simplicity and readability reasons, the code does not contain many optmizations, sanity checks and comprehensive error detection.


## Application workflow
To start the application, [Docker Desktop]("https://www.docker.com/products/docker-desktop/") is required.
The application will run throuh the `docker compose` command:
```
docker compose up --build
```

### This goes through few steps:

### 1) Docker build
An image will be built, starting from the official `Python:3.11` image, the code is copied in the image and few basic libraries are installed.
After the intial steps, a full test is called upon the code, to prevent a corrupted running.
At the end of the building process, the command to run the app with Python is defined and the port `8000` is defined as listening port.

### 2) App initialization
As soon as the app starts, the app does some initializing process:
- a `SQLite3` DB is initialized. Main table is created;
- a default/provided `CSV file` gets loaded and checked;
- the images contained in the CSV file get then read, resized, color mapped and stored into the DB;
- the API service starts listening.

### 3) API endpoints
We will be using the local address, provided by the endpoint automatically.

1) GET Image
```
http://0.0.0.0:8000/image/?depth=9001
```
This call will return the image, from the DB, at the depth indicated in the parameter (9001 as example)

2) GET Images in range
```
http://0.0.0.0:8000/images?depth_min=9000&depth_max=9030
```
This call in one of the `main objectives` of the exercise. It allows to call the endpoint and get all the images within a specified range of depths, using the parameters `depth_min` and `depth_max`.
The images are returned as an array of `base64` strings. The assumption is that the client can decode and use them as required. This allows a simple, clean and testable solution to send multiple images in one answer.

3) POST new CSV
```
http://0.0.0.0:8000/add
```
This is a protected endpoint, which allows users to add or replace image frames into the current running DB.
The *Authorization* header needs to be in the call, with the value provided in the .*env* file (*ANTONIO*).
The CSV file must be passed in the body, as standard text file, with the name `csv_file`.
The call returns some metadata around the process, like *nr of invalid lines*, *inserted images* and *overall status*.


### TESTS
Pytest and a folder, called `tests` has been created, to support the tests driven programming methodology, and to guardantee a better quality of the application.
There are 2 tests which get executed automatically, running the command:
```
pytest /app
```

The `first test`, *test_image_resize_and_encode()*, will:
- load the `test.csv` file;
- load and process the only image in the file (10 rows, including the headers);
- convert the image into a base64 string and finally check with the expected value.

The `second test`, *test_encode_and_store_in_db()*, will do almost the same things for the first one, but passing by the storing and reading from the DB, to ensure its expected functionalities.


### Image Processing
For simplicity, the PIL library has been used, along with its simple and standard ways to process images, like applying resizing and color mapping.

The assumption of the structure of the provided CSV file is that it contains image frames, spread on multiple rows. 
In each row, it contains:
- column1/depth: **depth** and **image single pixel slice** (1x200px), separated by a dot. As long as each following row contains the same depth, it belongs to the same image frame for that specific depth.
- column1-column200: contains the single slice of the image, each column the grey scale value of the pixel on that position.
