from flask import Blueprint, request, jsonify, render_template
from models.interview import create_interview, save_answers, get_interview
import uuid

interview_bp = Blueprint("interview", __name__)


@interview_bp.route("/interview/create", methods=["GET"])
def create_page():
    return render_template("index.html")


@interview_bp.route("/interview/<room_id>")
def room_page(room_id):
    interview = get_interview(room_id)
    if not interview:
        return render_template("index.html")
    return render_template("interview_room.html", room_id=room_id, interview=dict(interview))


@interview_bp.route("/api/interview/create", methods=["POST"])
def create():
    data = request.json
    room_id = data.get("room_id") or str(uuid.uuid4())[:8]
    role = data.get("role", "Software Developer")
    candidate_name = data.get("candidate_name", "Candidate")

    try:
        create_interview(room_id, role, candidate_name)
        return jsonify({"status": "created", "room_id": room_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@interview_bp.route("/api/interview/<room_id>", methods=["GET"])
def get(room_id):
    interview = get_interview(room_id)

    if interview:
        return jsonify(dict(interview))

    return jsonify({"error": "Interview not found"}), 404


@interview_bp.route("/api/interview/<room_id>/answers", methods=["POST"])
def save(room_id):
    data = request.json
    answers = data.get("answers", "")

    try:
        save_answers(room_id, answers)
        return jsonify({"status": "answers_saved"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500