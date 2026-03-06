rooms = {}


def add_user_to_room(room_id, user_sid):
    if room_id not in rooms:
        rooms[room_id] = set()
    rooms[room_id].add(user_sid)


def remove_user_from_room(room_id, user_sid):
    if room_id in rooms:
        rooms[room_id].discard(user_sid)
        if not rooms[room_id]:
            del rooms[room_id]


def get_room_users(room_id):
    return list(rooms.get(room_id, []))


def get_room_count(room_id):
    return len(rooms.get(room_id, set()))


def room_exists(room_id):
    return room_id in rooms and len(rooms[room_id]) > 0
