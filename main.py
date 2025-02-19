from pprint import pprint
from rocketchat_API.APIExceptions import RocketExceptions
import ldap3.core.exceptions
from requests import sessions
from connections import rocket, ldap
from func import json_read, json_write, log_all
from general_message import GeneralMessage
from user_sort import handle_new_user, handle_current_user, get_all_team_members
import os


def main():
    with sessions.Session() as session:
        try:
            users = rocket.users_list().json()
            json_path = f"{str(os.path.dirname(os.path.realpath(__file__)))}/txtData.json"
            json_data = json_read(json_path)

            # Fetch all teams once
            all_teams = rocket.teams_list_all().json().get('teams', [])
            team_members = get_all_team_members(all_teams)

            if users['total'] > json_data['totalUsers']:
                json_data['totalUsers'] = users['total']
                new_users = list(filter(lambda x: ('guest' not in x['roles'] and 'bot' not in x['roles']), users['users']))

                if len(new_users) == 0:
                    gm = GeneralMessage()
                    msg_log = f'{gm.create_message()} - Total user data updated, no users added to groups'
                else:
                    for user in new_users:
                        handle_new_user(user, all_teams, team_members)
                    gm = GeneralMessage()
                    msg_log = gm.create_message()

                log_all(msg_log)
                json_write(json_path, json_data)
            else:
                for user in users['users']:
                    if 'bot' not in user['roles'] and user['username'] != 'super.admin':
                        handle_current_user(user, all_teams, team_members)
                gm = GeneralMessage()
                msg_log = gm.create_message()
                log_all(f'No new users - {msg_log}')

            session.close()

        except (ConnectionError,
                OSError,
                ConnectionResetError,
                TypeError,
                RocketExceptions.RocketException,
                RocketExceptions.RocketConnectionException,
                RocketExceptions.RocketAuthenticationException,
                ldap3.core.exceptions.LDAPSocketSendError) as err:
            log_all(err)
            session.close()


if __name__ == '__main__':
    main()