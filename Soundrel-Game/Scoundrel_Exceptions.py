class ResolveRoomError(Exception):
    """
    There was an issue resolving a room.
    """
    pass

class NotInRoomError(Exception):
    """
    resolve_room or skip_room were called while the player was not in a room
    """
    pass

class CanNotSkipRoomError(Exception):
    """
    skip_room was called while the player could not skip the current room (due to the rules preventing the player from skipping
    two rooms in a row).
    """
    pass

class InRoomError(Exception):
    """
    enter_room was called before the player resolved the currrent room.
    """
    pass

class GameOverError(Exception):
    """
    resolve_room, skip_room, or enter_room were called after the game has ended.
    """
    pass