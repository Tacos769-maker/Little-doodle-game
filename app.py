import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Shared server-side world state
world_blocks = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    # Send the current world state immediately to the newly joined player
    emit('load_world', world_blocks)

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
        
    # Broadcast the change to ALL connected players instantly
    emit('update_block', {'x': x, 'y': y, 'color': color}, broadcast=True)

@socketio.on('clear_board')
def handle_clear():
    global world_blocks
    world_blocks.clear()
    emit('clear_board', broadcast=True)

@socketio.on('mouse_move')
def handle_mouse_move(data):
    # Broadcast cursor positions to other players
    emit('update_cursor', {'id': request.sid, 'x': data['x'], 'y': data['y'], 'color': data['color']}, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
