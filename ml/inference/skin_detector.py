import os
import cv2
import numpy as np
from PIL import Image
from ml.inference.skin_analysis import (
    estimate_skin_tone_category,
    estimate_undertone,
    get_recommended_palettes
)
from ml.preprocessing.color_extraction import rgb_to_hex

_landmarker = None

def get_face_landmarker():
    """
    Initializes and caches the Google MediaPipe FaceLandmarker singleton
    with 478 3D dense facial landmarks for surgical cheek/forehead isolation.
    """
    global _landmarker
    if _landmarker is None:
        try:
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            task_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "models",
                "face_landmarker.task"
            )
            if os.path.exists(task_path):
                base_options = python.BaseOptions(model_asset_path=task_path)
                options = vision.FaceLandmarkerOptions(
                    base_options=base_options,
                    output_face_blendshapes=False,
                    output_facial_transformation_matrixes=False,
                    num_faces=1
                )
                _landmarker = vision.FaceLandmarker.create_from_options(options)
                print("MediaPipe FaceLandmarker: 478 3D landmark mesh initialized successfully.")
        except Exception as e:
            print(f"MediaPipe FaceLandmarker initialization notice: {e}")
            _landmarker = None
    return _landmarker

def analyze_face_skin(image_path: str) -> dict:
    """
    Extracts face skin tone and undertone from image using landmark-guided
    anatomical facial patch sampling (cheeks, forehead) and true CIELAB conversion.
    
    Pipeline:
    1. Primary: Google MediaPipe FaceLandmarker extracting 478 3D facial landmarks.
       Samples polygon patches from Left Cheek, Right Cheek, and Forehead, completely
       bypassing beard hair, lips, eyes, and background.
    2. Secondary Fallback: OpenCV Haar Cascade box detection with facial geometry heuristics.
    3. Tertiary Fallback: Central facial chromaticity ROI filtering.
    4. True CIELAB conversion via cv2.COLOR_BGR2LAB for calibrated perceptual luminance (L*)
       and chromatic axes (a* for red-green, b* for blue-yellow).
    5. 12-Season harmonic color palette generation.
    """
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        raise ValueError("Could not read image file.")
    
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    h, w, _ = img_rgb.shape
    
    skin_samples_bgr = []
    skin_samples_rgb = []
    method_used = "MediaPipe-FaceMesh-468"
    
    # 1. Primary Method: Google MediaPipe FaceLandmarker
    landmarker = get_face_landmarker()
    if landmarker is not None:
        try:
            import mediapipe as mp
            mp_image = mp.Image.create_from_file(image_path)
            res = landmarker.detect(mp_image)
            if res.face_landmarks and len(res.face_landmarks) > 0:
                lms = res.face_landmarks[0]
                
                # Cheek and forehead polygon landmark indices (dense 3D mesh):
                # Left cheek: [117, 118, 101, 50, 123, 147]
                l_pts = np.array([[int(lms[idx].x * w), int(lms[idx].y * h)] for idx in [117, 118, 101, 50, 123, 147]], dtype=np.int32)
                # Right cheek: [346, 347, 330, 280, 352, 376]
                r_pts = np.array([[int(lms[idx].x * w), int(lms[idx].y * h)] for idx in [346, 347, 330, 280, 352, 376]], dtype=np.int32)
                # Forehead: [10, 67, 109, 103, 338, 297, 284]
                f_pts = np.array([[int(lms[idx].x * w), int(lms[idx].y * h)] for idx in [10, 67, 109, 103, 338, 297, 284]], dtype=np.int32)
                
                mask = np.zeros((h, w), dtype=np.uint8)
                cv2.fillPoly(mask, [l_pts, r_pts, f_pts], 255)
                
                mesh_pixels_bgr = img_bgr[mask == 255]
                mesh_pixels_rgb = img_rgb[mask == 255]
                
                if len(mesh_pixels_bgr) >= 50:
                    skin_samples_bgr.append(mesh_pixels_bgr)
                    skin_samples_rgb.append(mesh_pixels_rgb)
        except Exception as e:
            print(f"MediaPipe inference notice: {e}")
            
    # 2. Secondary Fallback: OpenCV Cascade detection if MediaPipe had no landmarks
    if not skin_samples_bgr:
        method_used = "Facial-Landmark-Patches-Cascade"
        cascade_path = os.path.join(getattr(cv2.data, 'haarcascades', ''), 'haarcascade_frontalface_default.xml')
        face_detected = False
        
        if os.path.exists(cascade_path):
            try:
                face_cascade = cv2.CascadeClassifier(cascade_path)
                gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))
                if len(faces) > 0:
                    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                    (x, y, fw, fh) = faces[0]
                    face_detected = True
                    
                    cheek_l_bgr = img_bgr[int(y + 0.45*fh):int(y + 0.65*fh), int(x + 0.20*fw):int(x + 0.40*fw)]
                    cheek_l_rgb = img_rgb[int(y + 0.45*fh):int(y + 0.65*fh), int(x + 0.20*fw):int(x + 0.40*fw)]
                    cheek_r_bgr = img_bgr[int(y + 0.45*fh):int(y + 0.65*fh), int(x + 0.60*fw):int(x + 0.80*fw)]
                    cheek_r_rgb = img_rgb[int(y + 0.45*fh):int(y + 0.65*fh), int(x + 0.60*fw):int(x + 0.80*fw)]
                    forehead_bgr = img_bgr[int(y + 0.15*fh):int(y + 0.32*fh), int(x + 0.30*fw):int(x + 0.70*fw)]
                    forehead_rgb = img_rgb[int(y + 0.15*fh):int(y + 0.32*fh), int(x + 0.30*fw):int(x + 0.70*fw)]
                    
                    for p_bgr, p_rgb in [(cheek_l_bgr, cheek_l_rgb), (cheek_r_bgr, cheek_r_rgb), (forehead_bgr, forehead_rgb)]:
                        if p_bgr.size > 0:
                            skin_samples_bgr.append(p_bgr.reshape(-1, 3))
                            skin_samples_rgb.append(p_rgb.reshape(-1, 3))
            except Exception as e:
                print(f"Face cascade detection notice: {e}")
                
    # 3. Tertiary Fallback: Central facial chromaticity ROI
    if not skin_samples_bgr or np.vstack(skin_samples_bgr).shape[0] < 50:
        method_used = "Adaptive-Facial-Chromaticity-ROI"
        face_roi_bgr = img_bgr[int(h * 0.20):int(h * 0.65), int(w * 0.25):int(w * 0.75)]
        face_roi_rgb = img_rgb[int(h * 0.20):int(h * 0.65), int(w * 0.25):int(w * 0.75)]
        if face_roi_bgr.size > 0:
            pixels_bgr = face_roi_bgr.reshape(-1, 3)
            pixels_rgb = face_roi_rgb.reshape(-1, 3)
            r, g, b = pixels_rgb[:, 0], pixels_rgb[:, 1], pixels_rgb[:, 2]
            skin_mask = (r > g) & (g > b) & (r > 60)
            valid_bgr = pixels_bgr[skin_mask]
            valid_rgb = pixels_rgb[skin_mask]
            if len(valid_bgr) >= 30:
                skin_samples_bgr = [valid_bgr]
                skin_samples_rgb = [valid_rgb]
            else:
                skin_samples_bgr = [pixels_bgr]
                skin_samples_rgb = [pixels_rgb]
        else:
            skin_samples_bgr = [img_bgr.reshape(-1, 3)]
            skin_samples_rgb = [img_rgb.reshape(-1, 3)]
            
    all_pixels_bgr = np.vstack(skin_samples_bgr)
    all_pixels_rgb = np.vstack(skin_samples_rgb)
    
    # 4. Median RGB sampling
    r_med = float(np.median(all_pixels_rgb[:, 0]))
    g_med = float(np.median(all_pixels_rgb[:, 1]))
    b_med = float(np.median(all_pixels_rgb[:, 2]))
    sample_hex = rgb_to_hex((r_med, g_med, b_med))
    
    # 5. True CIELAB Conversion using cv2.cvtColor
    b_med_val = float(np.median(all_pixels_bgr[:, 0]))
    g_med_val = float(np.median(all_pixels_bgr[:, 1]))
    r_med_val = float(np.median(all_pixels_bgr[:, 2]))
    bgr_sample = np.uint8([[[int(b_med_val), int(g_med_val), int(r_med_val)]]])
    lab_sample = cv2.cvtColor(bgr_sample, cv2.COLOR_BGR2LAB)
    
    # In OpenCV: L in [0, 255] -> map to [0, 100]
    L_cielab = float(lab_sample[0, 0, 0]) * 100.0 / 255.0
    a_cielab = float(lab_sample[0, 0, 1])  # 128 is neutral
    b_cielab = float(lab_sample[0, 0, 2])  # 128 is neutral (>128 yellow/warm, <128 blue/cool)
    
    # 6. Scientific CIELAB categorization
    estimated_skin_tone = estimate_skin_tone_category(L_cielab)
    
    # Undertone from CIELAB b* and a* balance
    yellow_deviation = b_cielab - 128.0
    red_deviation = a_cielab - 128.0
    
    if yellow_deviation > 8.0 and yellow_deviation >= (red_deviation - 2.0):
        estimated_undertone = "warm"
    elif red_deviation > 12.0 and yellow_deviation < 6.0:
        estimated_undertone = "cool"
    else:
        estimated_undertone = "neutral"
        
    palette_data = get_recommended_palettes(estimated_undertone, estimated_skin_tone)
    
    return {
        "estimated_skin_tone": estimated_skin_tone,
        "estimated_undertone": estimated_undertone,
        "sample_hex": sample_hex,
        "suggested_palettes": palette_data["palettes"],
        "primary_palette": palette_data["primary_palette"],
        "cielab_metrics": {
            "L_star": round(L_cielab, 1),
            "a_star": round(a_cielab, 1),
            "b_star": round(b_cielab, 1),
            "method": method_used
        },
        "requires_confirmation": True
    }
