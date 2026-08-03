from flask import Flask, render_template
from flask_socketio import SocketIO, emit, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# Initialize SocketIO with gevent async mode and cross-origin permissions
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# Server-side world state dictionary to store blocks
world_blocks = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    # Send the current world state to the newly connected player
    emit('load_world', world_blocks)
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('place_block')
def handle_place_block(data):
    x = data['x']
    y = data['y']
    color = data['color']
    key = f"{x},{y}"

    if color is None:
        if key in world_blocks:
            del world_blocks[key]
    else:
        world_blocks[key] = color

    # Broadcast the block update to everyone including sender
    emit('update_block', {'x': x, 'y': y, 'color': color}, broadcast=True)

@socketio.on('clear_board')
def handle_clear_board():
    global world_blocks
    world_blocks = {}
    emit('clear_board', broadcast=True)

@socketio.on('mouse_move')
def handle_mouse_move(data):
    # Broadcast cursor movement to other players
    emit('update_cursor', {
        'id': request.sid,
        'x': data['x'],
        'y': data['y'],
        'color': data['color']
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
