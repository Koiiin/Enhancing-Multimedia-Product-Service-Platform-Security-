import os

class Config:
    SECRET_KEY = 'your-very-secret-key-1234567890'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = 'uploads/'  
    ENCRYPTED_FOLDER = 'encrypted_videos/'
    TEMP_FOLDER = 'temp/'  

    ALLOWED_EXTENSIONS = {'mp4', 'mp3'}
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # giới hạn 100MB
