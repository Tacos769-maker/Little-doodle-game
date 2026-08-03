from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

grid_state = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('load_world', grid_state)

@socketio.on('place_block')
def handle_place_block(data):
    x = data['x']
    y = data['y']
    color = data['color']
    
    key = f"{x},{y}"
    if color is None:
        if key in grid_state:
            del grid_state[key]
    else:
        grid_state[key] = color
        
    emit('update_block', {'x': x, 'y': y, 'color': color}, broadcast=True)

@socketio.on('clear_board')
def handle_clear():
    grid_state.clear()
    emit('clear_board', broadcast=True)

@socketio.on('mouse_move')
def handle_mouse_move(data):
    emit('update_cursor', {'id': request.sid, 'x': data['x'], 'y': data['y'], 'color': data['color']}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)