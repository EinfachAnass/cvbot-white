import os

folder_path = '/home/anass/Desktop/SoSe25/RAML/GitRAML/cvbot-white/data/no_ball'  # Make sure this path is correct
start_index = 400

# Get all files, filter by extensions (including wrongly named ".peg")
files = sorted([
    f for f in os.listdir(folder_path)
    if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(('.jpg', '.jpeg', '.peg'))
])

# Rename each file
for i, filename in enumerate(files):
    old_path = os.path.join(folder_path, filename)
    new_filename = f"img{start_index + i}.jpg"  # Normalize all to .jpg
    new_path = os.path.join(folder_path, new_filename)

    os.rename(old_path, new_path)
    print(f"Renamed: {filename} -> {new_filename}")

print("Renaming complete.")
