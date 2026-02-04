from datetime import datetime

def extract_features(event: dict) -> dict:
    """
    Extrait les caractéristiques (features) d'un log pour alimenter l'Anomaly Detector.
    """
    message = event.get("message", "") or ""
    timestamp_str = event.get("timestamp", datetime.now().isoformat())

    features = {
        "has_failed": 1 if "failed" in message.lower() else 0,
        "msg_len": len(message),
        "hour": 0,
        "is_http": 0,
        "is_error": 0,
    }

    # Feature temporelle
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        features["hour"] = dt.hour
    except Exception:
        pass

    # HTTP / Apache
    if event.get("log_type") in ("http", "apache") or "HTTP/" in message:
        features["is_http"] = 1
        # Tentative de récupérer status_code s'il existe déjà
        status_code = event.get("status_code")
        if status_code is None:
            # Sinon, on essaie d'extraire le code HTTP depuis la ligne Apache
            # Exemple: ... "GET /path HTTP/1.1" 404 437 ...
            parts = message.split('"')
            if len(parts) >= 3:
                tail = parts[2].strip().split()
                if tail:
                    try:
                        status_code = int(tail[0])
                    except Exception:
                        status_code = 200
            else:
                status_code = 200

        try:
            features["is_error"] = 1 if int(status_code) >= 400 else 0
        except Exception:
            features["is_error"] = 0

    return features
