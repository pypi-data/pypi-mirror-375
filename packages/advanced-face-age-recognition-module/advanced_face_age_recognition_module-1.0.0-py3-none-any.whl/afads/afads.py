import math
import time
from dataclasses import dataclass, asdict
from typing import Optional, Tuple, Union, Dict, Any, List

import cv2
import numpy as np
from insightface.app import FaceAnalysis

@dataclass
class AFADSConfig:
    age_sigma_years: float = 6.0
    prob_over18_threshold: float = 0.85
    min_detection_score: float = 0.5
    face_selection: str = "best"  # "largest" | "best" | "first"
    min_face_width_px: int = 80
    min_image_variance: float = 15.0
    redact_crops_in_result: bool = True

@dataclass
class AFADSResult:
    over_18: bool
    prob_over_18: float
    estimated_age: float
    estimated_age_ci95: Tuple[float, float]
    face_box_xywh: Tuple[int, int, int, int]
    detection_score: float
    warnings: List[str]
    timing_ms: float
    debug: Optional[Dict[str, Any]] = None

class AFADS:
    """Advanced Face Age Detection System (local, on-device)."""
    def __init__(self, config: Optional[AFADSConfig] = None, providers: Optional[list] = None):
        self.config = config or AFADSConfig()
        self.providers = providers or ["CPUExecutionProvider"]
        self.app = FaceAnalysis(name="buffalo_l", providers=self.providers)
        self.app.prepare(ctx_id=0, det_size=(640, 640))

    @staticmethod
    def _to_bgr(img: Union[str, np.ndarray]) -> np.ndarray:
        if isinstance(img, str):
            bgr = cv2.imread(img, cv2.IMREAD_COLOR)
            if bgr is None:
                raise ValueError(f"Could not read image from path: {img}")
            return bgr
        elif isinstance(img, np.ndarray):
            if img.ndim == 2:
                return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            if img.shape[2] == 3:
                return img
            if img.shape[2] == 4:
                return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            raise ValueError("Unsupported ndarray image shape.")
        else:
            raise TypeError("img must be a file path or a numpy array")

    @staticmethod
    def _normal_cdf(x: float) -> float:
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    def _prob_age_geq(self, mean: float, sigma: float, threshold_age: float) -> float:
        if sigma <= 0:
            return 1.0 if mean >= threshold_age else 0.0
        z = (threshold_age - mean) / sigma
        return 1.0 - self._normal_cdf(z)

    def _pick_face(self, faces: list, img_w: int, img_h: int) -> Optional[Any]:
        if not faces:
            return None

        def score_face(f):
            x1, y1, x2, y2 = [int(v) for v in f.bbox]
            w, h = x2 - x1, y2 - y1
            area = w * h
            return (float(getattr(f, 'det_score', 0.0)) * 0.7
                    + (area / (img_w * img_h + 1e-6)) * 0.3)

        if self.config.face_selection == "largest":
            return max(faces, key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]))
        elif self.config.face_selection == "best":
            return max(faces, key=lambda f: score_face(f))
        else:
            return faces[0]

    def assess(self, img: Union[str, np.ndarray], return_dict: bool = True) -> Union[AFADSResult, Dict[str, Any]]:
        t0 = time.time()
        warnings: List[str] = []
        bgr = self._to_bgr(img)

        if float(np.var(bgr)) < self.config.min_image_variance:
            warnings.append("Low image variance; possible flat/spoof input.")

        h, w = bgr.shape[:2]
        faces = self.app.get(bgr)

        if not faces:
            res = AFADSResult(
                over_18=False,
                prob_over_18=0.0,
                estimated_age=-1.0,
                estimated_age_ci95=(-1.0, -1.0),
                face_box_xywh=(0,0,0,0),
                detection_score=0.0,
                warnings=["No face detected."],
                timing_ms=(time.time()-t0)*1000.0,
                debug=None
            )
            return asdict(res) if return_dict else res

        face = self._pick_face(faces, w, h)
        x1, y1, x2, y2 = [int(v) for v in face.bbox]
        det_score = float(getattr(face, 'det_score', 0.0))
        fw = x2 - x1

        if det_score < self.config.min_detection_score:
            warnings.append(f"Low detection score ({det_score:.2f}).")
        if fw < self.config.min_face_width_px:
            warnings.append(f"Face too small ({fw}px < {self.config.min_face_width_px}px).")

        est_age = float(getattr(face, "age", -1.0))
        if est_age <= 0:
            warnings.append("Model did not return an age; try higher-res face.")
            prob_18 = 0.0
            ci_low, ci_high = -1.0, -1.0
        else:
            sigma = self.config.age_sigma_years
            ci_low = max(0.0, est_age - 1.96 * sigma)
            ci_high = est_age + 1.96 * sigma
            prob_18 = self._prob_age_geq(est_age, sigma, 18.0)

        over_18 = bool(prob_18 >= self.config.prob_over18_threshold)

        debug_payload = None
        if not self.config.redact_crops_in_result:
            crop = bgr[max(y1,0):max(y2,0), max(x1,0):max(x2,0)]
            _, crop_jpg = cv2.imencode(".jpg", crop, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            debug_payload = {"face_crop_jpg_bytes": crop_jpg.tobytes()}

        result = AFADSResult(
            over_18=over_18,
            prob_over_18=float(prob_18),
            estimated_age=est_age,
            estimated_age_ci95=(float(ci_low), float(ci_high)),
            face_box_xywh=(int(x1), int(y1), int(x2-x1), int(y2-y1)),
            detection_score=det_score,
            warnings=warnings,
            timing_ms=(time.time()-t0)*1000.0,
            debug=debug_payload
        )
        return asdict(result) if return_dict else result
