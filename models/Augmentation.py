import imgaug.augmenters as iaa   # https://imgaug.readthedocs.io/en/latest/
import cv2                        # https://pypi.org/project/opencv-python/
import glob                       # importing this library to access all the files in the folder
import os                         # Creating files in the system

print ("packages imported successfully")

#1. Load data set
images = []   
images_path = glob.glob(r"C:\Users\serve\project\CATBOT\Image_augmentation\Image_data\*")  # Change folder root
# img = cv2.imread(r"C:\Users\serve\project\CATBOT\Image_augmentation\Image_data\dog.jpg") # To read single image

for img_pth in images_path:    # loop to read and store images
    img = cv2.imread(img_pth)
    images.append(img)

# 2. Image augmentation
augmentation = iaa.Sequential([
    #1. Flip 
    iaa.Sometimes(0.7,
                  iaa.Fliplr(1),  # Horizontal flipping
                  iaa.Flipud(1), # Vertical flipping
    ),

    #2. Affine
    iaa.Affine(translate_percent= {"x":(-0.2, 0.2), "y":(-0.2, 0.2)},
                #rotate=(-30,30),   # commended to ensure the use of rotate function seperatly
                scale= (0.5,1.5)),

    #3. Rotate
    iaa.Sometimes(0.7,iaa.Rotate()),

    #4. Multiply [used to make image brigth or dark using channels]
    iaa.Multiply((0.8 , 1.2)),

    #4. Linearcontrast
    iaa.LinearContrast((0.6 , 1.4)),

    # Perform methods below only sometimes
    iaa.Sometimes(0.5, 
        #5. GaussianBlur
        iaa.GaussianBlur((0.0 , 3.0)) )
])


# 3. Set output folder
output_dir = r"C:\Users\serve\project\CATBOT\Image_augmentation\Augmented_output"
os.makedirs(output_dir, exist_ok=True)

# 4. Save a specific number of augmented batches
count = 0  
num_batches = 0  
max_images = 3000   # Change the value if you want more OUTPUT data

while count <= max_images:
    augmented_images = augmentation(images=images)
    for idx, img in enumerate(augmented_images):
        filename = f"aug_{count}_{num_batches}.jpg"
        save_path = os.path.join(output_dir, filename)
        cv2.imwrite(save_path, img)
        print(f"Saved: {save_path}")
        count += 1

        if count % 5 == 0:
            num_batches += 1
        if count == max_images:
            print(f"\n Done! {count} augmented images saved.")
            break  # Breaks the inner for-loop

    # If count has reached the max, break the while-loop
    if count == max_images:
        break
    
print(f"\n Total {count} images saved to: {output_dir}")