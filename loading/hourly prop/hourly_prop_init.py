import os

# construct new folder 'img'
new_folder = "prop"

if os.path.exists(new_folder):
    pass
else:
    os.makedirs(new_folder)