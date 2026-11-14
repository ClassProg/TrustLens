def get_disagreement(image_id=None):
    # Only return grader statistics for a verified RIGA image identifier.
    return {"available": False, "graders": None, "agreement": None, "level": None}
