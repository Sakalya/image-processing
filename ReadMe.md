# Image processing app

Image processing app supports following operations:

1) POST new CSV
```
http://0.0.0.0:8000/add
```
This is a protected endpoint, which allows users to add or replace image frames into the current running DB.
The *Authorization* header needs to be in the call, with the value provided in the .*env* file (*DUMMY_TOKEN*).
The CSV file must be passed in the body, as standard text file, with the name `csv_file`.
The call returns some metadata around the process, like *nr of invalid lines*, *inserted images* and *overall status*.

2) GET Images in range
```
http://0.0.0.0:8000/images?depth_min=9000&depth_max=9020
```
The images are returned as an array of `base64` strings. The assumption is that the client can decode and use them as required. This allows a simple, clean and testable solution to send multiple images in one answer.

3) GET Image
```
http://0.0.0.0:8000/image/?depth=9001
```
This call will return the image, from the DB, at the depth indicated in the parameter (9001 as example)

# Architectural Pattern Used

1) MVC Pattern - This app uses MVC(Model View Controller) pattern where controller, 
services and database access classes are separated from one another.

## How to run application
To start the application, docker is required.
The application will run throuh the `docker compose` command:
```
docker compose up --build
```

### TESTS
Pytest and a folder, called `tests` has been created, to support the tests driven programming methodology, and to guardantee a better quality of the application.
There are 2 tests which get executed automatically, running the command:
```
pytest /app
```
