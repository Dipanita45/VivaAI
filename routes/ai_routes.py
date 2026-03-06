from flask import Blueprint, request, jsonify
from ai.question_engine import generate_question
from ai.tts_engine import generate_voice
from ai.report_engine import generate_report
from models.interview import save_report

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/api/ai/question", methods=["POST"])
def question():
    data = request.json
    role = data.get("role", "Software Developer")
    answer = data.get("answer")
    question_history = data.get("question_history", [])

    try:
        question_text = generate_question(role, answer, question_history)
        audio_url = generate_voice(question_text)

        return jsonify({
            "question": question_text,
            "audio": audio_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/api/ai/report", methods=["POST"])
def report():
    data = request.json
    role = data.get("role", "Software Developer")
    qa_history = data.get("qa_history", [])
    room_id = data.get("room_id")

    try:
        report_text = generate_report(role, qa_history)

        if room_id:
            import json
            save_report(room_id, report_text, json.dumps(qa_history))

        return jsonify({"report": report_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500