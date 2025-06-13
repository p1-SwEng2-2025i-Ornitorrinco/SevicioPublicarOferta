import os, uuid

def save_image(upload_file, folder="images") -> str:
    ext = os.path.splitext(upload_file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(folder, filename)
    with open(path, "wb") as f:
        f.write(upload_file.file.read())
    return f"/images/{filename}"
