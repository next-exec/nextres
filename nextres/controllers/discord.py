from flask import flash, render_template, request
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.discord import discord, make_discord_blueprint
from flask_login import current_user, login_required
from requests import delete, put

from nextres.constants import FLASH_ERROR, FLASH_SUCCESS
from nextres.controllers.auth import AuthController
from nextres.database.oauth import db, OAuth

GUILDS_API = 'https://discordapp.com/api/guilds/'


class DiscordController:
    def __init__(self, app):
        authorization = {'Authorization': 'Bot {}'.format(app.config['DISCORD_BOT_TOKEN'])}
        blueprint = make_discord_blueprint(app.config['DISCORD_CLIENT_ID'], app.config['DISCORD_CLIENT_SECRET'],
                                           ['guilds.join', 'identify'], redirect_to='account_discord',
                                           login_url='/discord/login',
                                           storage=SQLAlchemyStorage(OAuth, db.session, user=current_user))
        app.register_blueprint(blueprint)

        @oauth_authorized.connect_via(blueprint)
        def handle_authorized(_, token):
            join_guild()

        def join_guild():
            user = discord.get('/api/users/@me').json()

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
