from flask_socketio import emit, join_room, leave_room

# Track room membership: room_id -> set of session IDs
_rooms: dict = {}


def _add_to_room(room_id, sid):
    _rooms.setdefault(room_id, set()).add(sid)


def _remove_from_room(room_id, sid):
    if room_id in _rooms:
        _rooms[room_id].discard(sid)
        if not _rooms[room_id]:
            del _rooms[room_id]


def _count_in_room(room_id):
    return len(_rooms.get(room_id, set()))


def register_signaling_events(socketio):

    @socketio.on("join-room")
    def on_join(data):
        from flask import request as flask_request
        room = data["room"]
        sid = flask_request.sid

        join_room(room)
        _add_to_room(room, sid)

        count = _count_in_room(room)

        # Tell joining user if they're first (initiator) or second
        emit("room-joined", {
            "room": room,
            "is_initiator": count == 1
        })

        # Notify other existing users
        emit("user-joined", {"room": room}, to=room, include_self=False)

    @socketio.on("offer")
    def on_offer(data):
        emit("offer", data, to=data["room"], include_self=False)

    @socketio.on("answer")
    def on_answer(data):
        emit("answer", data, to=data["room"], include_self=False)

    @socketio.on("ice-candidate")
    def on_ice_candidate(data):
        emit("ice-candidate", data, to=data["room"], include_self=False)

    @socketio.on("leave-room")
    def on_leave(data):
        from flask import request as flask_request
        room = data["room"]
        sid = flask_request.sid

        leave_room(room)
        _remove_from_room(room, sid)
        emit("user-left", {"room": room}, to=room)

    @socketio.on("disconnect")
    def on_disconnect():
        from flask import request as flask_request
        sid = flask_request.sid
        # Remove from all rooms this SID was in
        for room_id in list(_rooms.keys()):
            if sid in _rooms.get(room_id, set()):
                _remove_from_room(room_id, sid)