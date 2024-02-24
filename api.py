from functools import wraps
import json
import logging
import uuid
import tailwind
from battleship.server import GameServer, StateUpdater, is_finished, is_started
from flask import Flask, make_response, render_template, request, url_for

from battleship.view import View


def configure_routing(app: Flask, updater: StateUpdater):
    logger = app.logger
    logger.setLevel(logging.INFO)
    server = GameServer(updater, logger)
    view = View(tailwind.config)

    def get_cookie(key):
        def decorator(func):
            @wraps(func)
            def inner(*args, **kwargs):
                cookie = request.cookies.get(key)
                return func(cookie, *args, **kwargs)
            
            return inner
        
        return decorator

    def set_cookie(key, factory):
        def decorator(func):
            @wraps(func)
            def inner(*args, **kwargs):
                cookie = request.cookies.get(key)
                value = cookie if cookie else factory()
                response = make_response(func(value, *args, **kwargs))
                response.set_cookie(key, value)
                return response
            
            return inner
        
        return decorator

    @app.get('/')
    @set_cookie('player-id', lambda: str(uuid.uuid4()))
    def lobby(_):
        return render_template('index.html', page='create')
    
    @app.post('/')
    def create():
        game = server.new_game()
        
        response = make_response()
        response.headers.add_header('HX-Redirect', url_for('game', game=game))
        return response
    
    @app.get('/games/<game>')
    @set_cookie('player-id', lambda: str(uuid.uuid4()))
    def game(player, game):
        state = server.get(game)
        if not is_finished(state) and not is_started(state):
            logger.info("Game %s has not started, player %s to join", game, player)
            return render_template('index.html', page='join', game=game)
        else:
            return render_template('index.html', page='state', game=game, **view.render(state, player))
        
    @app.get('/games/<game>/join')
    @get_cookie('player-id')
    def load_join(player, game):
        state = server.get(game)
        return render_template('htmx/join.html', game=game, **view.render(state, player))
    
    @app.post('/games/<game>')
    @get_cookie('player-id')
    def join(player, game):
        name = request.form['player-name']
        state = server.join(game, player, name)
        if not is_started(state):
            return render_template('components/join.html', game=game)
        else:
            return render_template('components/state.html', game=game, **view.render(state, player))
    
    @app.get('/games/<game>/poll')
    @get_cookie('player-id')
    def poll(player, game):
        state = server.get(game)
        return render_template('htmx/poll.html', game=game, **view.render(state, player))
    
    @app.post('/games/<game>/target')
    @get_cookie('player-id')
    def target(player, game):
        state = server.get(game)
        board = int(request.args.get('board'))
        position = int(request.args.get('x')), int(request.args.get('y'))
        if state.players[board].id != player:
            state = server.target(game, board, position)
            
        return render_template('components/state.html', game=game, **view.render(state, player))
    
    return app
