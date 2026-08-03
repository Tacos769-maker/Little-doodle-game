import os
import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

DATA_FILE = 'world.json'

def load_world_from_disk():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_world_to_disk(world):
    with open(DATA_FILE, 'w') as f:
        json.dump(world, f)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    world_blocks = load_world_from_disk()
    emit('load_world', world_blocks)

@socketio.on('place_block')
def handle_place_block(data):
    x = data['x']
    y = data['y']
    color = data['color']
    key = f"{x},{y}"
    
    world_blocks = load_world_from_disk()
    
    if color is None:
        if key in world_blocks:
            del world_blocks[key]
    else:
        world_blocks[key] = color
        
    save_world_to_disk(world_blocks)
        
    emit('update_block', {'x': x, 'y': y, 'color': color}, broadcast=True)

@socketio.on('clear_board')
def handle_clear():
    save_world_to_disk({})
    emit('clear_board', broadcast=True)

@socketio.on('mouse_move')
def handle_mouse_move(data):
    emit('update_cursor', {'id': request.sid, 'x': data['x'], 'y': data['y'], 'color': data['color']}, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
