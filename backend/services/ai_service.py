from pathlib import Path


def detect_forgery(image_path):
    """
    Run the exact same model prediction used by the
    terminal test and convert the result into the
    format expected by verification.py.
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    # Keep the lightweight API routes deployable without the local ML runtime.
    try:
        from ai_models.forgery_detector.predict_classifier import predict
    except ImportError as error:
        raise RuntimeError(
            "The forgery model runtime is not installed in this deployment. "
            "Run the AI backend locally or deploy it separately with TensorFlow."
        ) from error

    prediction = predict(str(image_path))

    print("MODEL PREDICTION:", prediction)

    fake_probability = float(
        prediction["forgery_probability"]
    )

    genuine_probability = (
        100.0 - fake_probability
    )

    if prediction["result"] == "genuine":
        status = "GENUINE"
        message = (
            "The AI model detected a higher "
            "probability of a genuine document."
        )
    else:
        status = "FAKE"
        message = (
            "The AI model detected a higher "
            "probability of forgery. "
            "Manual verification is recommended."
        )

    return {
        "result": prediction["result"],
        "confidence": prediction["confidence"],

        "fake_probability": round(
            fake_probability,
            2
        ),

        "genuine_probability": round(
            genuine_probability,
            2
        ),

        "status": status,
        "message": message,
    }