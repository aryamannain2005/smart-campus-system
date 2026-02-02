# Installation Notes

## Dependencies Installation - February 1, 2026

### Issue Encountered
The original `requirements.txt` included `dlib` and `face-recognition` packages which failed to build on macOS with Apple Silicon (ARM) architecture due to compilation issues:
- Missing CMake (resolved by installing via Homebrew)
- Missing `fp.h` header file during dlib compilation (known issue on ARM macOS)

### Solution Applied
1. **Installed CMake** via Homebrew: `brew install cmake`
2. **Modified requirements.txt** to replace problematic packages:
   - Removed: `face-recognition>=1.3.0` 
   - Removed: `dlib>=19.24`
   - Added: `opencv-contrib-python>=4.8` (extended OpenCV with additional modules)
   - Added: `deepface>=0.0.79` (modern face recognition library with multiple backends)
   - Added: `mtcnn>=0.1.1` (Multi-task Cascaded Convolutional Networks for face detection)

### Successfully Installed Packages
- Django 6.0.1
- djangorestframework 3.16.1
- Pillow 12.1.0
- numpy 2.4.2
- opencv-python 4.13.0.90
- opencv-contrib-python 4.13.0.90
- deepface 0.0.98
- mtcnn 1.0.0
- tensorflow 2.20.0
- celery 5.6.2
- redis 7.1.0
- django-cors-headers 4.9.0

### Code Migration Required
The face recognition code in the project will need to be updated to use DeepFace or MTCNN instead of the `face-recognition` library:

**Old approach (face_recognition):**
```python
import face_recognition
image = face_recognition.load_image_file("person.jpg")
face_locations = face_recognition.face_locations(image)
face_encodings = face_recognition.face_encodings(image, face_locations)
```

**New approach (DeepFace):**
```python
from deepface import DeepFace
result = DeepFace.verify("person1.jpg", "person2.jpg")
faces = DeepFace.extract_faces("person.jpg")
embedding = DeepFace.represent("person.jpg")
```

**Alternative (MTCNN):**
```python
from mtcnn import MTCNN
import cv2
detector = MTCNN()
image = cv2.imread("person.jpg")
faces = detector.detect_faces(image)
```

### Next Steps
1. Update face recognition code in `face_recognition/ai_engine.py` to use DeepFace or MTCNN
2. Test the face detection and recognition functionality
3. Run migrations: `python manage.py migrate`
4. Start the development server: `python manage.py runserver`
