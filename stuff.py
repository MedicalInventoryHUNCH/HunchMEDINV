import cv2
import face_recognition

def visualize_facial_recognition(input_path, output_path):
    # Load the image
    image = face_recognition.load_image_file(input_path)
    
    # Detect face locations and landmarks
    face_locations = face_recognition.face_locations(image)
    face_landmarks_list = face_recognition.face_landmarks(image)
    
    # Convert the image from RGB to BGR format (OpenCV compatible)
    bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    # Draw bounding boxes around detected faces
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(bgr_image, (left, top), (right, bottom), (0, 255, 0), 2)
    
    # Draw facial landmarks for each face
    for face_landmarks in face_landmarks_list:
        for feature, points in face_landmarks.items():
            # Draw lines between consecutive landmark points
            for i in range(len(points) - 1):
                cv2.line(bgr_image, points[i], points[i+1], (0, 0, 255), 1)
    
    # Save the output image
    cv2.imwrite(output_path, bgr_image)
    print(f"Processed image saved to {output_path}")

# Specify the paths directly in the code
input_image_path = "/home/hunch/PycharmProjects/HunchPythonNFCREAL/pictures/face0.jpg"   # Change this to the path of your input image
output_image_path = "/home/hunch/PycharmProjects/HunchPythonNFCREAL/pictures/test.jpg" # Change this to your desired output image path

visualize_facial_recognition(input_image_path, output_image_path)
