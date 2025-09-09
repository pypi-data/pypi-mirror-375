from flask import Blueprint, request, jsonify
from media_agent_mcp.video.omni_human import generate_video_from_omni_human

omni_human_bp = Blueprint("omni_human", __name__)

@omni_human_bp.post("/generate-video-from-omni-human")
def generate_video():
    """
    Generates a video from an image and audio using the Omni Human API.
    """
    try:
        data = request.get_json(silent=True) or {}
        image_url = data.get("image_url")
        audio_url = data.get("audio_url")

        if not image_url or not audio_url:
            return jsonify({
                "status": "error",
                "data": None,
                "message": "Fields image_url and audio_url are required"
            }), 400

        video_url = generate_video_from_omni_human(image_url, audio_url)

        return jsonify({
            "status": "success",
            "data": {
                "video_url": video_url
            },
            "message": "Video generated successfully"
        })

    except Exception as e:
        return jsonify({"status": "error", "data": None, "message": str(e)}), 500