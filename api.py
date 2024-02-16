from functools import wraps
import logging
import uuid
import tailwind
from battleship.server import GameServer, StateUpdater, can_move, is_started
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
    def create():
        game = server.new_game()
        return redirect(url_for('join', game=game))
    
    @app.get('/<game>')
    @set_cookie('player-id', lambda: str(uuid.uuid4()))
    def join(player, game):
        game = int(game)
        if not server.exists(game):
            logger.info("Game %s does not exist. Redirecting...", game)
            return redirect(url_for('create'))
        
        logger.info("Player %s has joined game %s", player, game)
        state = server.join(server.get(game), player)
        if not is_started(state):
            logger.info("Game %s has not started, polling state", game)
            strategy = 'poll'
        elif not can_move(state, player):
            logger.info("Player %s awaits turn, polling state", player)
            strategy = 'poll'
        else:
            strategy = 'state'

        return render_template('index.html', game=game, strategy=strategy, **view.render(state, player))
    
    @app.get('/<game>/poll')
    @get_cookie('player-id')
    def poll(player, game):
        game = int(game)
        state = server.get(game)
        if is_started(state) and can_move(state, player):
            logger.info("Player %s can take turn, stop polling", player)
            strategy = 'state'
        else:
            strategy = 'poll'

        return render_template(f'partials/{strategy}.html', game=game, **view.render(state, player))
    
    @app.post('/<game>/target')
    @get_cookie('player-id')
    def target(player, game):
        game = int(game)
        state = server.get(game)
        board = int(request.args.get('board'))
        position = int(request.args.get('x')), int(request.args.get('y'))
        if state.players[board].id != player:
            state = server.target(state, board, position)
        
        return render_template('partials/poll.html', game=game, **view.render(state, player))
    
    return app
