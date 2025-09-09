"""

FFHQ-style face alignment using InsightFace landmarks
"""
from __future__ import annotations
import builtins as __builtins__
import cupy as cp
import cupyx as cupyx
import pixtreme as px
__all__ = ['align_face_ffhq', 'cp', 'cupyx', 'px']
def align_face_ffhq(img: cp.ndarray, face_landmarks: cp.ndarray, output_size: int = 256, transform_size: int = 1024, enable_padding: bool = True) -> cp.ndarray:
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
__test__: dict = {}
