from pprint import pprint
from ldap3 import SUBTREE
from func import system_time, log_all
from classes import Teams, ITMsg
from connections import rocket, ldap

teams = Teams()
itmsg = ITMsg()

# List of usernames to ignore for removal from groups
ignore_removal_users = []

def get_all_team_members(all_teams):
    team_members = {}
    for team in all_teams:
        response = rocket.teams_members(team_id=team['_id']).json()
        members = response.get('members', [])
        team_members[team['name']] = [member.get('user', {}).get('_id') for member in members]
    return team_members

def get_user_teams(user_id, team_members):
    user_teams = []
    for team_name, members in team_members.items():
        if user_id in members:
            user_teams.append(team_name)
    return user_teams

def is_user_disabled_in_ldap(user_dn):
    search_filter = f"(&(objectclass=user)(distinguishedName={user_dn})(userAccountControl:1.2.840.113556.1.4.803:=2))"
    _, _, response, _ = ldap.search(
        # fill in search_base
        search_base='',
        search_filter=search_filter,
        attributes=['distinguishedName'],
        search_scope=SUBTREE)
    return bool(response)

def is_user_disabled_in_rocketchat(username):
    user_info = rocket.users_info(username=username).json()
    return user_info.get('user', {}).get('active', True) is False

def handle_new_user(user, all_teams, team_members):
    if user['username'] in itmsg.support or user['username'] in itmsg.sysadmins:
        return

    conn = ldap
    if not conn.bind():
        return

    # Fetch the user's location in LDAP
    search_filter = f"(&(objectclass=user)(sAMAccountName={user['username']}))"
    _, _, response, _ = conn.search(
        # fill in search_base
        search_base='',
        search_filter=search_filter,
        attributes=['sAMAccountName', 'distinguishedName'],
        search_scope=SUBTREE)

    if not response:
        return

    ldap_user_dn = response[0]['attributes']['distinguishedName']

    if is_user_disabled_in_ldap(ldap_user_dn) or is_user_disabled_in_rocketchat(user['username']):
        return

    target_groups = [team for team in teams.teams if ldap_user_dn.rfind(team.dn) != -1]

    if target_groups:
        current_teams = get_user_teams(user['_id'], team_members)

        for target_group in target_groups:
            if target_group.name not in current_teams:
                team_id = next((team['_id'] for team in all_teams if team['name'] == target_group.name), None)
                if team_id:
                    response = rocket.teams_add_members(team_id=team_id, members=[{'userId': user['_id']}]).json()
                    log = f"{system_time()} - Added {user['username']} to {target_group.name} - Response: {response}"
                    log_all(log)
                else:
                    log = f"{system_time()} - Team ID not found for {target_group.name}"
                    log_all(log)

    rocket.channels_invite('[general_channel]', user['_id'])
    conn.unbind()
    return

def handle_current_user(user, all_teams, team_members):
    if user['username'] in itmsg.support or user['username'] in itmsg.sysadmins:
        return

    conn = ldap
    if not conn.bind():
        return

    current_teams = get_user_teams(user['_id'], team_members)

    current_teams = [team_name for team_name in current_teams if any(team.name == team_name for team in teams.teams)]

    search_filter = f"(&(objectclass=user)(sAMAccountName={user['username']}))"
    _, _, response, _ = conn.search(
        # fill in search_base
        search_base='',
        search_filter=search_filter,
        attributes=['sAMAccountName', 'distinguishedName'],
        search_scope=SUBTREE)

    if not response:
        return

    ldap_user_dn = response[0]['attributes']['distinguishedName']

    if is_user_disabled_in_ldap(ldap_user_dn) or is_user_disabled_in_rocketchat(user['username']):
        return

    if not current_teams:
        log = f"{system_time()} - User {user['username']} with DN {ldap_user_dn} is part of no teams"
        log_all(log)
        handle_new_user(user, all_teams, team_members)
        return

    target_teams = [team for team in teams.teams if ldap_user_dn.rfind(team.dn) != -1]

    if target_teams:
        for target_team in target_teams:
            if target_team.name not in current_teams:
                team_id = next((team['_id'] for team in all_teams if team['name'] == target_team.name), None)
                if team_id:
                    response = rocket.teams_add_members(team_id=team_id, members=[{'userId': user['_id']}]).json()
                    log = f"{system_time()} - Added {user['username']} to {target_team.name} - Response: {response}"
                    log_all(log)
                else:
                    log = f"{system_time()} - Team ID not found for {target_team.name}"
                    log_all(log)

        for team_name in current_teams:
            if team_name not in [team.name for team in target_teams] and user['username'] not in ignore_removal_users:
                team_id = next((team['_id'] for team in all_teams if team['name'] == team_name), None)
                if team_id:
                    response = rocket.teams_remove_member(team_id=team_id, user_id=user['_id']).json()
                    log = f"{system_time()} - Removed {user['username']} from {team_name} - Response: {response}"
                    log_all(log)
                else:
                    log = f"{system_time()} - Team ID not found for {team_name}"
                    log_all(log)

    rocket.channels_invite('[general_channel]', user['_id'])
    conn.unbind()
    return