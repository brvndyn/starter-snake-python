import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    color = "#00FF00"

    return start_response(color)




def decideMove(data):
    height = data["board"]["height"]
    width = data["board"]["width"]

    badCoords = []

    for x in range(width):
        bad = (x, -1)
        badCoords.append(bad)
        bad = (x, height)
        badCoords.append(bad)

    for y in range(width):
        bad = (-1, y)
        badCoords.append(bad)
        bad = (width, y)
        badCoords.append(bad)


    for snake in data["board"]["snakes"]:
        for xy in snake["body"]:
            bad = (xy["x"], xy["y"])
            badCoords.append(bad)


    head = data["you"]["body"][0]
    possibleMoves = []

    # left
    coord = (head["x"]-1, head["y"])
    if coord not in badCoords:
        possibleMoves.append("left")

    # right
    coord = (head["x"]+1, head["y"])
    if coord not in badCoords:
        possibleMoves.append("right")

    # up
    coord = (head["x"], head["y"]-1)
    if coord not in badCoords:
        possibleMoves.append("up")

    # down
    coord = (head["x"], head["y"]+1)
    if coord not in badCoords:
        possibleMoves.append("down")



    # final decision

    if len(possibleMoves) > 0:
        finalMove = foodSearch(possibleMoves, data)
        print (foodSearch(possibleMoves, data))
        if (finalMove == "no food"):
            finalMove = random.choice(possibleMoves)

    else:
        # doesn't really matter
        finalMove = random.choice(["left", "right", "up", "down"])

    print("badCoords={}".format(badCoords))
    print("possibleMoves={}".format(possibleMoves))
    print("finalMove={}".format(finalMove))
    return finalMove



def foodSearch(possibleMoves, data):
    head = data["you"]["body"][0]
    closest = {}
    closestDif = 300
    for food in data["board"]["food"]:
        differenceX = head["x"] - food["x"]
        differenceY = head["y"] - food["y"]

        differenceTotal = abs(differenceX)+abs(differenceY)

        if (differenceTotal < closestDif):
            closest = food
            print("")
            print(closest)
            print("")
            closestDif = differenceTotal

    if (head["x"] > closest["x"]):
        for dir in possibleMoves:
            if (dir == "left"):
                return "left"

    if (head["x"] < closest["x"]):
        for dir in possibleMoves:
            if (dir == "right"):
                return "right"

    if (head["y"] > closest["y"]):
        for dir in possibleMoves:
            if (dir == "up"):
                return "up"

    if (head["y"] < closest["y"]):
        for dir in possibleMoves:
            if (dir == "down"):
                return "down"

    return "no food"


@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data))

    direction = decideMove(data)

    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
