from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from flask_socketio import SocketIO, send, emit
from project.chat.forms import UrlForm
from project.models import ChatRoom
from project import db, app, socketio
from base64 import b64encode
from os import urandom





chat_blueprint = Blueprint(
    'chat',
    __name__,
    template_folder = "templates"
)


current_url = ''
@chat_blueprint.route('/', methods=['GET', 'POST'])
def index():

    form = UrlForm(request.form)
    if request.method == 'POST':
        #Query Database to see if url is already in the database. If in database then it is currently in use
        #If it isn't in the database then connect to url and add it to the database so no one else can create the same room
        user_url = ChatRoom(request.form['url'])
        db_url = ChatRoom.query.filter_by(url=user_url.url).first()

        if db_url == None:
            #add new url to database
            current_url = user_url.url
            print(current_url)
            url = ChatRoom(user_url.url)
            db.session.add(url)
            db.session.commit()
            return redirect(url_for('chat.chat', user_route=user_url.url))
        else:
            return render_template('/chat/index.html', form=form)
    return render_template('/chat/index.html', form=form)

@chat_blueprint.route('/<user_route>')
def chat(user_route):
    #if user_route is in database and user is allowed in room allow the connection
    return render_template('/chat/chat.html')






#SOCKET EVENTS






# Keep track of connected users
class Socket:
    def __init__(self, sid):
        self.sid = sid
        self.connected = True
        self.username = sid


sockets = []

##look in array and find the sid with the request.sid, send username with the message.


@socketio.on('connect')
def add_socket():
    this_socket = (Socket(request.sid))
    sockets.append(this_socket)
    print(sockets[0])
    print(len(sockets))

@socketio.on('disconnect')
def remove_socket():
    socket_to_remove = sockets.index(request.sid)
    sockets.pop(socket_to_remove)
    print(socket_to_remove)
    print(len(sockets))

@socketio.on('username_message')
def handle_username_message(msg):
    print(msg['data'])
    for socket in sockets:
        if request.sid == socket.sid:
            socket.username = msg['data']
            print(socket.username)

    emit('username_message', {'data': msg['data']}, broadcast=True)


@socketio.on('message')
def handle_message(msg):
    print(msg)
    for socket in sockets:
        if request.sid == socket.sid:
            username = socket.username
            send(username, broadcast=True)



