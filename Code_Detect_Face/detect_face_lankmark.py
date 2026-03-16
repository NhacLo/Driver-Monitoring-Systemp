import cv2
import numpy as np
import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_PATH = r"C:\project_cua_nhac\ver3\face_landmarker.task"
LEFT_EYE_IDX  = [263, 249, 390, 373, 374, 380, 381, 382, 362,
                 466, 388, 387, 386, 385, 384, 398]

RIGHT_EYE_IDX = [33, 7, 163, 144, 145, 153, 154, 155, 133,
                 246, 161, 160, 159, 158, 157, 173]

LEFT_IRIS_IDX  = [474, 475, 476, 477]
RIGHT_IRIS_IDX = [469, 470, 471, 472]

RIGHT_EYE_EAR_IDX = [33, 160, 158, 133, 153, 144]
LEFT_EYE_EAR_IDX  = [362, 385, 387, 263, 373, 380]

# Neutral pose (nhìn thẳng) để đưa góc về gần 0
NEUTRAL_R = None

# Làm mượt góc
ANGLE_STATE = {
    "yaw": None,
    "pitch": None,
    "roll": None,
}
SMOOTH_ALPHA = 0.25

def reset_angle_state():
    global ANGLE_STATE
    ANGLE_STATE = {
        "yaw": None,
        "pitch": None,
        "roll": None,
    }


def normalize_angle_deg(angle):
    return (angle + 180.0) % 360.0 - 180.0


def smooth_angle(name, angle):
    prev = ANGLE_STATE[name]
    if prev is None:
        ANGLE_STATE[name] = angle
        return angle

    delta = normalize_angle_deg(angle - prev)
    value = normalize_angle_deg(prev + SMOOTH_ALPHA * delta)
    ANGLE_STATE[name] = value
    return value


def create_landmarker():
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )
    return vision.FaceLandmarker.create_from_options(options)


def get_landmarks_2d(face_landmarks, image_width, image_height, indices):
    points_2d = []
    for i in indices:
        x = face_landmarks[i].x * image_width
        y = face_landmarks[i].y * image_height
        points_2d.append((x, y))
    return np.array(points_2d, dtype=np.float64)

def get_eye_landmarks(face_landmarks, image_width, image_height):
    left_eye = get_landmarks_2d(face_landmarks, image_width, image_height, LEFT_EYE_EAR_IDX)
    right_eye = get_landmarks_2d(face_landmarks, image_width, image_height, RIGHT_EYE_EAR_IDX)
    left_iris = get_landmarks_2d(face_landmarks, image_width, image_height, LEFT_IRIS_IDX)
    right_iris = get_landmarks_2d(face_landmarks, image_width, image_height, RIGHT_IRIS_IDX)

    return {
        "left_eye": left_eye,
        "right_eye": right_eye,
        "left_iris": left_iris,
        "right_iris": right_iris
    }


def draw_eye_landmarks(frame, eye_landmarks, draw_index=False):
    def draw_points(points, color, prefix=""):
        for i, (x, y) in enumerate(points):
            x, y = int(x), int(y)
            cv2.circle(frame, (x, y), 2, color, -1)
            if draw_index:
                cv2.putText(
                    frame,
                    f"{prefix}{i}",
                    (x + 3, y - 3),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35,
                    color,
                    1,
                    cv2.LINE_AA
                )

    def draw_closed_poly(points, color):
        pts = points.astype(np.int32)
        for i in range(len(pts)):
            p1 = tuple(pts[i])
            p2 = tuple(pts[(i + 1) % len(pts)])
            cv2.line(frame, p1, p2, color, 1)

    #draw_points(eye_landmarks["left_eye"], (0, 255, 0), "LE")
    #draw_points(eye_landmarks["right_eye"], (0, 255, 0), "RE")
    #draw_points(eye_landmarks["left_iris"], (255, 0, 0), "LI")
    #draw_points(eye_landmarks["right_iris"], (255, 0, 0), "RI")

    draw_closed_poly(eye_landmarks["left_eye"], (0, 255, 255))
    draw_closed_poly(eye_landmarks["right_eye"], (0, 255, 255))
    draw_closed_poly(eye_landmarks["left_iris"], (255, 255, 0))
    draw_closed_poly(eye_landmarks["right_iris"], (255, 255, 0))

    return frame

def get_face_model_3d():
    model_points = np.array([
        (0.0,    0.0,    0.0),      # Nose tip
        (0.0,  -63.6,  -12.5),      # Chin
        (-43.3, 32.7,  -26.0),      # Left eye outer corner
        (43.3,  32.7,  -26.0),      # Right eye outer corner
        (-28.9, -28.9, -24.1),      # Left mouth corner
        (28.9,  -28.9, -24.1)       # Right mouth corner
    ], dtype=np.float64)
    return model_points


def get_camera_matrix(image_width, image_height):
    focal_length = image_width
    center = (image_width / 2, image_height / 2)

    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype=np.float64)

    return camera_matrix


def rotation_matrix_to_euler_angles_cv(R):
    proj = np.hstack((R, np.zeros((3, 1), dtype=np.float64)))
    _, _, _, _, _, _, euler = cv2.decomposeProjectionMatrix(proj)

    pitch = normalize_angle_deg(float(euler[0, 0]))
    yaw = normalize_angle_deg(float(euler[1, 0]))
    roll = normalize_angle_deg(float(euler[2, 0]))

    return pitch, yaw, roll


def draw_pose_axis(frame, camera_matrix, dist_coeffs, rvec, tvec, nose_2d):
    axis_3d = np.array([
        [50, 0, 0],   # X
        [0, 50, 0],   # Y
        [0, 0, 50]    # Z
    ], dtype=np.float64)

    axis_2d, _ = cv2.projectPoints(axis_3d, rvec, tvec, camera_matrix, dist_coeffs)
    axis_2d = axis_2d.reshape(-1, 2).astype(int)

    p0 = tuple(np.int32(nose_2d))
    px = tuple(axis_2d[0])
    py = tuple(axis_2d[1])
    pz = tuple(axis_2d[2])

    cv2.line(frame, p0, px, (0, 0, 255), 2)   # X - do
    cv2.line(frame, p0, py, (0, 255, 0), 2)   # Y - xanh la
    cv2.line(frame, p0, pz, (255, 0, 0), 2)   # Z - xanh duong


def head_pose_estimation(frame, face_landmarks):
    global NEUTRAL_R

    h, w = frame.shape[:2]

    # nose, chin, left eye, right eye, left mouth, right mouth
    idx = [1, 152, 33, 263, 61, 291]

    image_points = get_landmarks_2d(face_landmarks, w, h, idx)
    model_points = get_face_model_3d()
    camera_matrix = get_camera_matrix(w, h)
    dist_coeffs = np.zeros((4, 1), dtype=np.float64)

    success, rvec, tvec = cv2.solvePnP(
        model_points,
        image_points,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE
    )

    if not success:
        return frame, None

    if hasattr(cv2, "solvePnPRefineLM"):
        rvec, tvec = cv2.solvePnPRefineLM(
            model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            rvec,
            tvec
        )

    R_abs, _ = cv2.Rodrigues(rvec)

    if NEUTRAL_R is None:
        R_use = R_abs
    else:
        R_use = NEUTRAL_R.T @ R_abs

    pitch, yaw, roll = rotation_matrix_to_euler_angles_cv(R_use)

    pitch = smooth_angle("pitch", pitch)
    yaw = smooth_angle("yaw", yaw)
    roll = smooth_angle("roll", roll)

    # Vẽ trục tuyệt đối từ pose gốc
    nose_2d = image_points[0]
    draw_pose_axis(frame, camera_matrix, dist_coeffs, rvec, tvec, nose_2d)

    text = f"Yaw: {yaw:.1f}  Pitch: {pitch:.1f}  Roll: {roll:.1f}"
    cv2.putText(
        frame,
        text,
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    pose = {
        "pitch": float(pitch),
        "yaw": float(yaw),
        "roll": float(roll),
        "rvec": rvec,
        "tvec": tvec,
        "R_abs": R_abs,
        "image_points": image_points
    }

    return frame, pose


def process_frame(frame, landmarker, timestamp_ms):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    result = landmarker.detect_for_video(mp_image, timestamp_ms)

    if not result.face_landmarks:
        return frame, None

    face = result.face_landmarks[0]
    frame, pose = head_pose_estimation(frame, face)

    h, w = frame.shape[:2]
    eye_landmarks = get_eye_landmarks(face, w, h)
    frame = draw_eye_landmarks(frame, eye_landmarks, draw_index=False)
    right_ear = calculate_ear(eye_landmarks["right_eye"])
    left_ear = calculate_ear(eye_landmarks["left_eye"])
    ear = (left_ear + right_ear) / 2.0

    return frame, pose, ear


def classify_head_pose(yaw, pitch, yaw_thresh=15, pitch_thresh=12):
    if abs(yaw) < yaw_thresh and abs(pitch) < pitch_thresh:
        return "LOOK_STRAIGHT"
    elif yaw <= -yaw_thresh:
        return "LOOK_LEFT"
    elif yaw >= yaw_thresh:
        return "LOOK_RIGHT"
    elif pitch <= -pitch_thresh:
        return "LOOK_UP"
    elif pitch >= pitch_thresh:
        return "LOOK_DOWN"
    return "UNKNOWN"

def calculate_ear(eye_pts):
    """
    eye_pts: numpy array shape (6, 2)
    thứ tự điểm: [p1, p2, p3, p4, p5, p6]
    """
    A = np.linalg.norm(eye_pts[1] - eye_pts[5])  # p2-p6
    B = np.linalg.norm(eye_pts[2] - eye_pts[4])  # p3-p5
    C = np.linalg.norm(eye_pts[0] - eye_pts[3])  # p1-p4

    if C < 1e-6:
        return 0.0

    return float((A + B) / (2.0 * C))

def classify_eye_state(ear, ear_threshold=0.18):
    if ear < ear_threshold:
        return "closed"
    else:
        return "open"

def main():
    global NEUTRAL_R

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Khong mo duoc webcam.")
        return

    landmarker = create_landmarker()

    try:
        neutral_set = False
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Khong doc duoc frame.")
                break

            # frame = cv2.flip(frame, 1)

            timestamp_ms = int(time.time() * 1000)
            output_frame, pose, ear = process_frame(frame, landmarker, timestamp_ms)

            if pose is not None:
                # Tự động lấy NEUTRAL_R từ frame đầu tiên có nhận diện mặt
                if not neutral_set:
                    NEUTRAL_R = pose["R_abs"].copy()
                    reset_angle_state()
                    neutral_set = True

                label = classify_head_pose(pose["yaw"], pose["pitch"])
                label_eye = classify_eye_state(ear)

                cv2.putText(
                    output_frame,
                    f"Direction: {label}, Eye: {label_eye}",
                    (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2
                )

                print(
                    f"Yaw={pose['yaw']:.2f}, "
                    f"Pitch={pose['pitch']:.2f}, "
                    f"Roll={pose['roll']:.2f}, "
                    f"Label={label}, "
                    f"EAR={ear:.3f}"
                )

            cv2.imshow("Head Pose Estimation", output_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        landmarker.close()


if __name__ == "__main__":
    main()