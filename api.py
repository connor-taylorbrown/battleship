from functools import wraps
import logging
import uuid
import tailwind
from battleship.server import GameServer, StateUpdater, can_move, has_joined, is_finished, is_started
from flask import Flask, make_response, render_template, redirect, request, url_for

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
        return render_template('index.html', action='create')
    
    @app.get('/<game>')
    @set_cookie('player-id', lambda: str(uuid.uuid4()))
    def game(player, game):
        state = server.get(game)
        if is_finished(state):
            logger.info("Game %s finished, do not poll", game)
            action = 'state'
        elif has_joined(state, player) and not is_started(state):
            logger.info("Game %s has not started, polling state", game)
            action = 'poll'
        elif not has_joined(state, player):
            logger.info("Game %s has not started, player %s to join", game, player)
            return render_template('index.html', action='join', game=game)
        elif not can_move(state, player):
            logger.info("Player %s awaits turn, polling state", player)
            action = 'poll'
        else:
            action = 'state'

        return render_template('index.html', action=action, game=game, **view.render(state, player))
    
    @app.post('/')
    @get_cookie('player-id')
    def create(player):
        name = request.form['player-name']
        game = server.new_game(player, name)
        
        response = make_response()
        response.headers.add_header('HX-Redirect', url_for('join', game=game))
        return response
    
    @app.post('/<game>')
    @get_cookie('player-id')
    def join(player, game):
        name = request.form['player-name']
        state = server.join(game, player, name)
        return render_template(f'partials/poll.html', game=game, **view.render(state, player))
    
    @app.get('/<game>/poll')
    @get_cookie('player-id')
    def poll(player, game):
        state = server.get(game)
        if is_started(state) and can_move(state, player):
            logger.info("Player %s can take turn, stop polling", player)
            strategy = 'state'
        elif is_finished(state):
            logger.info("Game %s finished, stop polling", game)
            strategy = 'state'
        else:
            strategy = 'poll'

        return render_template(f'partials/{strategy}.html', game=game, **view.render(state, player))
    
    @app.post('/<game>/target')
    @get_cookie('player-id')
    def target(player, game):
        state = server.get(game)
        board = int(request.args.get('board'))
        position = int(request.args.get('x')), int(request.args.get('y'))
        if state.players[board].id != player:
            state = server.target(game, board, position)
        
        if is_finished(state):
            logger.info("Game %s won, do not poll", game)
            strategy = 'state'
        else:
            logger.info("Player %s ends turn, start polling", player)
            strategy = 'poll'

        return render_template(f'partials/{strategy}.html', game=game, **view.render(state, player))
    
    return app
