from PIL import Image
import logging
import base64
import io

logger = logging.getLogger('images')
logger.setLevel(logging.DEBUG)

# This class handles the image processing and base64 encoding/decoding
# It doesn't need to be a class, it could have been a series of functions
class ImageProcessor:
    def __init__(self):
        pass
    
    # This function reads the content of the CSV, where we have an image for every depth.
    # For each depth:
    # 1) it would undertsand the width and height of each image
    # 2) flatter the 2-layer array in a byte object
    # 3) generate an Image object, in grey scale, from the byte object
    # 4) apply a custom red/blu gradient colormap
    # 5) resize the image, keeping the ration
    # 6) encode the image into a base64 string
    # Note: It doesn't matter the height of each image, as long as it respect the number of column in the CSV file.
    #       It will still be resized to 150 pixel, with the right ratio for the height.
    def load_and_resize_images(self, images) -> dict:
        encoded_images = []
        for depth, image in images.items():
            height = len(image)
            # the width could also be variable, but controlled in the CSV size, during the load
            width = len(image[0])
            # logger.debug(f"{depth}: H{height}x{width}")

            # Create the PIL image, using just the byte conversion
            flat_data = [int(pixel) for row in image for pixel in row]
            image_data = bytes(flat_data)

            # Create the PIL Image - 'L' mode for grayscale
            image = Image.frombytes('L', (width, height), image_data)
            # Apply the color map to the image
            image = self.apply_custom_colormap(image)
            # Resize the image
            resized_image = self.resize_image(image=image)
            # Encode the image
            image_base64 = self.encode_image(resized_image)
            
            # Add the new created image to the array
            encoded_images.append([depth, image_base64])

        return encoded_images

    # Resizes the image to the new width, keeping the ratio.
    # If the ratio is < 1, then it keeps the same height
    def resize_image(self, image) -> Image:
        # Specify the new width you want
        new_width = 150
        # Calculate the new height to maintain the aspect ratio
        aspect_ratio = image.height / image.width
        new_height = int(new_width * aspect_ratio)
        # To prevent 0px height
        if aspect_ratio < 1:
             new_height = image.height
        # Resize the image, using the library itself
        return image.resize((new_width, new_height))
    
    # Simply decodes the base64 string into the bytecode and push it into a buffer to return as io
    def decode_image(self, image_base64):
        image_data = base64.b64decode(image_base64)
        # Creating the buffer to send back the file
        buffer = io.BytesIO(image_data)
        buffer.seek(0)
        return buffer
    
    # Encode a bytecode image into a base64 string
    def encode_image(self, image: Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        # Move to the start of the buffer
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    # This is just a sample mapping, which converts the 256 possible grey values into a red/blu gradient.
    def apply_custom_colormap(self, image: Image) -> Image:
        image = image.convert("P")
        colormap = [(int(255 * i / 255), 0, int(255 * (255 - i) / 255)) for i in range(256)]
        # putpalette to have an index of possible colors, rather than containing them directly in the pixel value
        image.putpalette([color for rgb in colormap for color in rgb])
        return image

    def read_images_from_csv(self,csv_file, validator):
        images = {}
        invalid_lines = []

        with open(csv_file, 'r') as file:
            for index, line in enumerate(file):
                line = line.strip().split(',')
                if index > 0 and validator.is_lines_valid(line=line):
                    depth, height = map(int, line[0].split('.'))
                    image_data = line[1:]

                    if depth not in images:
                        images[depth] = []
                    images[depth].append(image_data)
                else:
                    if index != 0:
                        logger.warning(f'Invalid Line at index {index}')
                        invalid_lines.append(index)

        logger.info("New data loaded in the DB")
        return images, invalid_lines
