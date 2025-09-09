"""
FFHQ-style face alignment using InsightFace landmarks
"""

from typing import Optional, Tuple

import cupy as cp
import pixtreme as px
import cupyx.scipy.ndimage


def align_face_ffhq(
    img: cp.ndarray,
    face_landmarks: cp.ndarray,
    output_size: int = 256,
    transform_size: int = 1024,
    enable_padding: bool = True
) -> cp.ndarray:
    """
    Align face using FFHQ algorithm with 5-point landmarks from InsightFace.
    
    Args:
        img: Input image (CuPy array in RGB format)
        face_landmarks: 5-point landmarks from InsightFace (CuPy array, shape: [5, 2])
                       Order: left_eye, right_eye, nose, left_mouth, right_mouth
        output_size: Output image size (default: 256)
        transform_size: Transform buffer size (default: 1024)
        enable_padding: Enable padding for better boundary handling (default: True)
    
    Returns:
        Aligned face image (CuPy array in RGB format)
    """
    # Extract landmark points
    lm = face_landmarks
    
    # Calculate eye and mouth positions
    eye_left = lm[0]
    eye_right = lm[1]
    mouth_left = lm[3]
    mouth_right = lm[4]
    
    # Calculate auxiliary vectors
    eye_avg = (eye_left + eye_right) * 0.5
    eye_to_eye = eye_right - eye_left
    mouth_avg = (mouth_left + mouth_right) * 0.5
    eye_to_mouth = mouth_avg - eye_avg
    
    # Choose oriented crop rectangle (FFHQ-style)
    x = eye_to_eye - cp.flipud(eye_to_mouth) * cp.array([-1, 1])
    x /= cp.linalg.norm(x)
    x *= max(cp.linalg.norm(eye_to_eye) * 2.0, cp.linalg.norm(eye_to_mouth) * 1.8)
    y = cp.flipud(x) * cp.array([-1, 1])
    c = eye_avg + eye_to_mouth * 0.1
    quad = cp.stack([c - x - y, c - x + y, c + x + y, c + x - y])
    qsize = cp.linalg.norm(x) * 2
    
    # Ensure img is float32 
    if img.dtype != cp.float32:
        img = px.to_float32(img)
    
    # Shrink if needed
    shrink = int(cp.floor(qsize / output_size * 0.5))
    if shrink > 1:
        h, w = img.shape[:2]
        rsize = (int(cp.rint(float(w) / shrink)), 
                 int(cp.rint(float(h) / shrink)))
        img = px.resize(img, rsize, interpolation=px.INTER_AREA)
        quad /= shrink
        qsize /= shrink
    
    # Crop
    border = max(int(cp.rint(qsize * 0.1)), 3)
    crop = (int(cp.floor(cp.min(quad[:,0]))), int(cp.floor(cp.min(quad[:,1]))), 
            int(cp.ceil(cp.max(quad[:,0]))), int(cp.ceil(cp.max(quad[:,1]))))
    h, w = img.shape[:2]
    crop = (max(crop[0] - border, 0), max(crop[1] - border, 0), 
            min(crop[2] + border, w), min(crop[3] + border, h))
    if crop[2] - crop[0] < w or crop[3] - crop[1] < h:
        img = img[crop[1]:crop[3], crop[0]:crop[2]]
        quad -= crop[0:2]
    
    # Pad if needed
    pad = (int(cp.floor(cp.min(quad[:,0]))), int(cp.floor(cp.min(quad[:,1]))), 
           int(cp.ceil(cp.max(quad[:,0]))), int(cp.ceil(cp.max(quad[:,1]))))
    h, w = img.shape[:2]
    pad = (max(-pad[0] + border, 0), max(-pad[1] + border, 0), 
           max(pad[2] - w + border, 0), max(pad[3] - h + border, 0))
    
    if enable_padding and max(pad) > border - 4:
        pad = cp.maximum(pad, int(cp.rint(qsize * 0.3)))
        img = cp.pad(img, ((pad[1], pad[3]), (pad[0], pad[2]), (0, 0)), mode='reflect')
        h, w, _ = img.shape
        y, x = cp.ogrid[:h, :w]
        y = y[:, cp.newaxis]
        x = x[cp.newaxis, :]
        mask = cp.maximum(1.0 - cp.minimum(x.astype(cp.float32) / pad[0], (w-1-x).astype(cp.float32) / pad[2]), 
                         1.0 - cp.minimum(y.astype(cp.float32) / pad[1], (h-1-y).astype(cp.float32) / pad[3]))
        mask = mask[:, :, cp.newaxis]
        blur = qsize * 0.02
        blurred = cupyx.scipy.ndimage.gaussian_filter(img, [blur, blur, 0])
        img += (blurred - img) * cp.clip(mask * 3.0 + 1.0, 0.0, 1.0)
        median_val = cp.median(img, axis=(0,1))
        img += (median_val - img) * cp.clip(mask, 0.0, 1.0)
        img = cp.clip(img, 0, 1)
        quad += pad[:2]
    
    # Transform using affine transformation (approximation of perspective)
    # Use three points from the quad for affine transformation
    src_pts = quad[:3].astype(cp.float32)
    dst_pts = cp.array([[0, 0], [0, transform_size], 
                        [transform_size, transform_size]], dtype=cp.float32)
    
    # Calculate affine transform matrix using least squares
    # M * [src_pts; 1] = dst_pts
    src_pts_h = cp.ones((3, 3))
    src_pts_h[:, :2] = src_pts
    
    # Solve for transformation matrix
    M = cp.linalg.lstsq(src_pts_h.T, dst_pts.T)[0].T[:2, :]
    
    # Apply affine transformation
    img = px.affine_transform(img, M, (transform_size, transform_size))
    
    # Resize if needed
    if output_size < transform_size:
        img = px.resize(img, (output_size, output_size), interpolation=px.INTER_AREA)
    
    return img