from app import read_images_from_csv
from services import image_service, database_service


# This test will:
# 1) load a fixed/test portion of the provided CSV (img at depth 9000)
# 2) convert the image into the Image object
# 3) process and resize the image
# 4) encode64 the image
# 5) check if the result is the expected one
def test_image_resize_and_encode():
    img_proc = image_service.ImageProcessor()
    correct_b64 = "iVBORw0KGgoAAAANSUhEUgAAAJYAAAAJCAMAAADn7yVGAAADAFBMVEUAAP8BAP4CAP0DAPwEAPsFAPoGAPkHAPgIAPcJAPYKAPULAPQMAPMNAPIOAPEPAPAQAO8RAO4SAO0TAOwUAOsVAOoWAOkXAOgYAOcZAOYaAOUbAOQcAOMdAOIeAOEfAOAgAN8hAN4iAN0jANwkANslANomANknANgoANcpANYqANUrANQsANMtANIuANEvANAwAM8xAM4yAM0zAMw0AMs1AMo2AMk3AMg4AMc5AMY6AMU7AMQ8AMM9AMI+AME/AMBAAL9BAL5CAL1DALxEALtFALpGALlHALhIALdJALZKALVLALRMALNNALJOALFPALBQAK9RAK5SAK1TAKxUAKtVAKpWAKlXAKhYAKdZAKZaAKVbAKRcAKNdAKJeAKFfAKBgAJ9hAJ5iAJ1jAJxkAJtlAJpmAJlnAJhoAJdpAJZqAJVrAJRsAJNtAJJuAJFvAJBwAI9xAI5yAI1zAIx0AIt1AIp2AIl3AIh4AId5AIZ6AIV7AIR8AIN9AIJ+AIF/AICAAH+BAH6CAH2DAHyEAHuFAHqGAHmHAHiIAHeJAHaKAHWLAHSMAHONAHKOAHGPAHCQAG+RAG6SAG2TAGyUAGuVAGqWAGmXAGiYAGeZAGaaAGWbAGScAGOdAGKeAGGfAGCgAF+hAF6iAF2jAFykAFulAFqmAFmnAFioAFepAFaqAFWrAFSsAFOtAFKuAFGvAFCwAE+xAE6yAE2zAEy0AEu1AEq2AEm3AEi4AEe5AEa6AEW7AES8AEO9AEK+AEG/AEDAAD/BAD7CAD3DADzEADvFADrGADnHADjIADfJADbKADXLADTMADPNADLOADHPADDQAC/RAC7SAC3TACzUACvVACrWACnXACjYACfZACbaACXbACTcACPdACLeACHfACDgAB/hAB7iAB3jABzkABvlABrmABnnABjoABfpABbqABXrABTsABPtABLuABHvABDwAA/xAA7yAA3zAAz0AAv1AAr2AAn3AAj4AAf5AAb6AAX7AAT8AAP9AAL+AAH/AADdLmX9AAAAT0lEQVR4nM3QwQ3AMAhDUe+/YRQlNkxSqHopC8C/WOL0BDQrc/GshW5HKVl3b3Q7SuYmkeh2lIKV4X9sT3wV01i8DJimsfJbA1lf01gexTyFN6AGN4RiqAAAAABJRU5ErkJggg=="
    image, invalid_line = read_images_from_csv('/app/tests/test.csv')
    image = img_proc.load_and_resize_images(images=image)

    test_b64 = image[0][1]
    assert correct_b64 == test_b64 and len(invalid_line) == 0


# This test is similar to the test_image_resize_and_encode
# But it will pass through the DB population and retrieval process.
# 1) load a fixed portion of the CSV (img at depth 9000)
# 2) convert the image into the Image object
# 3) process and resize the image
# 4) encode64 the image
# 5) load the image into DB
# 6) retrieve the image from the DB, using the same ID loaded at the first row
# 7) drop the table, just to not leave any trace for the app main run
# 8) check if the result from the DB is the same of the expected one
def test_encode_and_store_in_db():
    db = database_service.DbManager()
    img_proc = image_service.ImageProcessor()
    correct_b64 = "iVBORw0KGgoAAAANSUhEUgAAAJYAAAAJCAMAAADn7yVGAAADAFBMVEUAAP8BAP4CAP0DAPwEAPsFAPoGAPkHAPgIAPcJAPYKAPULAPQMAPMNAPIOAPEPAPAQAO8RAO4SAO0TAOwUAOsVAOoWAOkXAOgYAOcZAOYaAOUbAOQcAOMdAOIeAOEfAOAgAN8hAN4iAN0jANwkANslANomANknANgoANcpANYqANUrANQsANMtANIuANEvANAwAM8xAM4yAM0zAMw0AMs1AMo2AMk3AMg4AMc5AMY6AMU7AMQ8AMM9AMI+AME/AMBAAL9BAL5CAL1DALxEALtFALpGALlHALhIALdJALZKALVLALRMALNNALJOALFPALBQAK9RAK5SAK1TAKxUAKtVAKpWAKlXAKhYAKdZAKZaAKVbAKRcAKNdAKJeAKFfAKBgAJ9hAJ5iAJ1jAJxkAJtlAJpmAJlnAJhoAJdpAJZqAJVrAJRsAJNtAJJuAJFvAJBwAI9xAI5yAI1zAIx0AIt1AIp2AIl3AIh4AId5AIZ6AIV7AIR8AIN9AIJ+AIF/AICAAH+BAH6CAH2DAHyEAHuFAHqGAHmHAHiIAHeJAHaKAHWLAHSMAHONAHKOAHGPAHCQAG+RAG6SAG2TAGyUAGuVAGqWAGmXAGiYAGeZAGaaAGWbAGScAGOdAGKeAGGfAGCgAF+hAF6iAF2jAFykAFulAFqmAFmnAFioAFepAFaqAFWrAFSsAFOtAFKuAFGvAFCwAE+xAE6yAE2zAEy0AEu1AEq2AEm3AEi4AEe5AEa6AEW7AES8AEO9AEK+AEG/AEDAAD/BAD7CAD3DADzEADvFADrGADnHADjIADfJADbKADXLADTMADPNADLOADHPADDQAC/RAC7SAC3TACzUACvVACrWACnXACjYACfZACbaACXbACTcACPdACLeACHfACDgAB/hAB7iAB3jABzkABvlABrmABnnABjoABfpABbqABXrABTsABPtABLuABHvABDwAA/xAA7yAA3zAAz0AAv1AAr2AAn3AAj4AAf5AAb6AAX7AAT8AAP9AAL+AAH/AADdLmX9AAAAT0lEQVR4nM3QwQ3AMAhDUe+/YRQlNkxSqHopC8C/WOL0BDQrc/GshW5HKVl3b3Q7SuYmkeh2lIKV4X9sT3wV01i8DJimsfJbA1lf01gexTyFN6AGN4RiqAAAAABJRU5ErkJggg=="
    image, invalid_line = read_images_from_csv('/app/tests/test.csv')
    image = img_proc.load_and_resize_images(images=image)

    # Insert the image in the DB and then retrieve it
    db.insert_images(image)
    test_b64 = db.get_image(image[0][0])

    # drop the table before starting the actual program
    db.drop_table()

    assert test_b64 == correct_b64

