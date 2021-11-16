from flask import flash, render_template, request
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.discord import discord, make_discord_blueprint
from flask_login import current_user, login_required
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from requests import delete, put

from nextres.constants import FLASH_ERROR, FLASH_SUCCESS
from nextres.controllers.auth import AuthController
from nextres.database.models import OAuth
from nextres.database import db

GUILDS_API = 'https://discordapp.com/api/guilds/'


class DiscordController:
    def __init__(self, app):
        authorization = {'Authorization': 'Bot {}'.format(app.config['DISCORD_BOT_TOKEN'])}
        blueprint = make_discord_blueprint(app.config['DISCORD_CLIENT_ID'], app.config['DISCORD_CLIENT_SECRET'],
                                           scope=['guilds.join', 'identify'], redirect_to='account_discord',
                                           login_url='/discord/login',
                                           storage=SQLAlchemyStorage(OAuth, db.session, user=current_user))
        app.register_blueprint(blueprint)

        @app.route('/discord', methods=['GET', 'POST'])
        @login_required
        @AuthController.instance.authorize.in_group('residents')
        def account_discord():
            if request.method == 'POST':
                if '_method' in request.form and request.form['_method'] in ['PUT', 'DELETE']:
                    if request.form['_method'] == 'PUT':
                        join_guild()
                    elif request.form['_method'] == 'DELETE':
                        status_code = 200
                        try:
                            r = discord.post(
                                "/api/oauth2/token/revoke",
                                data={
                                    'client_id': app.config['DISCORD_CLIENT_ID'],
                                    'client_secret': app.config['DISCORD_CLIENT_SECRET'],
                                    'token': blueprint.token['access_token']
                                },
                                headers={"Content-Type": "application/x-www-form-urlencoded"}
                            )
                            status_code = r.status_code
                        except TokenExpiredError as e:
                            pass
                        if status_code == 200:
                            r = delete('{}{}/members/{}'
                                       .format(GUILDS_API, app.config['DISCORD_VERIFICATION_GUILD'],
                                               current_user.discord_id),
                                       headers=authorization)
                            if r.status_code == 204:
                                current_user.discord_id = None
                                current_user.discord_username = None
                                current_user.discord_discriminator = None
                                db.session.commit()
                                flash('Your Discord account has been disconnected successfully. To regain access to the '
                                      'Next House Discord server, please connect another account.', FLASH_SUCCESS)
                            else:
                                flash('An error occurred while disconnecting your Discord account. Please wait a bit and '
                                      'try again later. If this issue persists, please contact '
                                      '<a href="mailto:next-techchair@mit.edu">next-techchair@mit.edu</a> for assistance.',
                                      FLASH_ERROR)
                        else:
                            flash('An error occurred while disconnecting your Discord account. Please wait a bit and '
                                  'try again later. If this issue persists, please contact '
                                  '<a href="mailto:next-techchair@mit.edu">next-techchair@mit.edu</a> for assistance.',
                                  FLASH_ERROR)
                        del blueprint.token
                else:
                    flash('The server received an invalid request. Please wait a bit and try again later. If this '
                          'issue persists, please contact '
                          '<a href="mailto:next-techchair@mit.edu">next-techchair@mit.edu</a> for assistance.',
                          FLASH_ERROR)
            return render_template('discord.html', authorized=discord.authorized)

        @oauth_authorized.connect_via(blueprint)
        @login_required
        @AuthController.instance.authorize.in_group('residents')
        def handle_authorized(_, token):
            join_guild()

        def join_guild():
            try:
                # scope is actually such a cursed concept
                user = discord.get('/api/users/@me').json()
            except TokenExpiredError as e:
                flash('Your Discord token has expired. Please disconnnect and re-authenticate.', FLASH_ERROR)
                return

            if not current_user.discord_id:
                current_user.discord_id = user['id']
            elif current_user.discord_id != user['id']:
                flash('You re-authenticated with a Discord account different from the account linked to your account. '
                      'To connect a different account, disconnect your existing account first.', FLASH_ERROR)
                return

            current_user.discord_username = user['username']
            current_user.discord_discriminator = user['discriminator']
            db.session.commit()
            r = put('https://discordapp.com/api/guilds/{}/members/{}'
                    .format(app.config['DISCORD_VERIFICATION_GUILD'], user['id']),
                    json={
                        'access_token': discord.access_token,
                        'roles': [app.config['DISCORD_VERIFICATION_ROLE']],
                        'nick': current_user.kerberos
                    }, headers=authorization)
            if r.status_code == 204:
                r = put('https://discordapp.com/api/guilds/{}/members/{}/roles/{}'
                        .format(app.config['DISCORD_VERIFICATION_GUILD'], user['id'],
                                app.config['DISCORD_VERIFICATION_ROLE']), headers=authorization)
            if r.status_code not in [201, 204]:
                flash('There was an error granting you access to the Discord server. Please wait a bit and '
                      'click the "Rejoin" button below to try again. If this issue persists, please contact '
                      '<a href="mailto:next-techchair@mit.edu">next-techchair@mit.edu</a> for assistance.',
                      FLASH_ERROR)
                return
            flash('Success! You now have access to the Next House Discord server.', FLASH_SUCCESS)
            return
