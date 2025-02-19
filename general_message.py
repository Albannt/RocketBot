from config import rchat
from func import presence_translate, present, system_time
from connections import rocket, ldap
from ldap3 import SUBTREE
from pprint import pprint
from classes import itmsg, Teams

class GeneralMessage:
    def __init__(self):
        self.groups = (rocket.groups_list_all().json())['groups']
        self.category1 = []
        self.category2 = []
        self.ignore = ["OU="]  # Ignore these teams when making general message
        self.sec_groups = self.sec_groups()
        self.teams = Teams()

    def general_msg_block(self, team, group1, group2):
        block = []
        members = []
        all_members = 0
        members_json = rocket.groups_members(room_id=team.id).json()
        if 'members' in members_json:
            members = members_json['members']
        else:
            pprint(f'Error in {team.name}: {members_json}')

        for member in members:
            if member['name'] != 'Rocket Bot' and member['name'] != 'Super Admin': # Exclude Rocket Bot and Super Admin accounts
                all_members += 1
                if present(member['status']):
                    active_member = member['username']
                    # these ifs check if member is in certain security groups in AD, then adds info to their general msg status
                    if member['name'] in group1:
                        active_member += ' (sekretariat)'
                    if member['name'] in group2:
                        if member['name'].split(' ', 1)[0][-1] == 'a':
                            active_member += ' ([])' # add custom status for
                        else:
                            active_member += ' ([])' # add custom status for
                    active_member = presence_translate(f"{active_member} - {member['status']}")
                    block.append(active_member)

        sorted_block = sorted(list(map(lambda x: f'- @{x}', block)))
        if sorted_block.count(f'- @{team.boss}') > 0:
            sorted_block.insert(0, sorted_block.pop(sorted_block.index(f'- @{team.boss}')))

        present_str = f'{str(len(sorted_block))}/{str(all_members)}'
        sorted_block = '\n'.join(sorted_block)
        block = f'*{team.header.lower().title()}* {present_str}\n{sorted_block}'
        return block

    def it_block(self, team, header):
        block = []

        for member in team:
            presence = (rocket.users_get_presence(username=member).json())['presence']
            if present(presence):
                block.append(presence_translate(f'{member} - {presence}'))

        full_header = f'- *{header}* {str(len(block))}/{str(len(team))}'
        handles = '\n'.join(list(map(lambda x: ('- - @' + x), block)))
        block = f'{full_header}\n{handles}'
        return block

    def full_it_block(self):
        support_str = self.it_block(itmsg.support, '[name of IT section]')
        sysadmins_str = self.it_block(itmsg.sysadmins, '[name of IT section]')
        it_team = self.teams.get_team_by_id('[IT team ID]')

        it_boss_presence = (rocket.users_get_presence(username=it_team.boss).json())['presence']
        it_boss_handle = presence_translate(f"- @{it_team.boss} - {it_boss_presence}")

        block = f"\n*{it_team.header.lower().title()}*\n{it_boss_handle}\n{support_str}\n{sysadmins_str}"
        return block

    # custom status based on two security groups
    def sec_groups(self):
        def sec_group_list(searchbase):
            try:
                conn = ldap
                if not conn.bind():
                    return []
                search_filter = '(objectclass=group)'
                _, _, response, _ = conn.search(
                    search_base=searchbase,
                    search_filter=search_filter,
                    attributes=['member'],
                    search_scope=SUBTREE)

                members = response[0]['attributes']['member']
                members = list(map(lambda a: a.split(',', 1)[0].split('=', 1)[1], members))
                return members
            except RecursionError:
                return []

        group1 = ''
        group2 = ''

        sec_groups_list = {
            'group1': sec_group_list(group1),
            'group2': sec_group_list(group2)
        }

        return sec_groups_list

    def create_message(self):
        for group in self.groups:
            for team in self.teams.teams:
                if team.dn not in self.ignore:
                    if group['name'] == team.name and team.name == 'IT':
                        full_block = self.full_it_block()
                        self.category1.append(full_block)
                    elif group['name'].lower() == team.name.lower():
                        full_block = self.general_msg_block(team, self.sec_groups['group1'], self.sec_groups['group2'])
                        match team.category:
                            case 'category1':
                                self.category1.append(full_block)
                            case 'category2':
                                self.category2.append(full_block)

        sorted_category1 = '\n\n'.join(sorted(self.category1))
        sorted_category2 = '\n\n'.join(sorted(self.category2))
        sorted_users = f"---*[category1]*---\n{sorted_category1}\n\n\n---*[category2]*---\n\n{sorted_category2}" # headers of two sections, defined by the category field in teams list
        rocket.chat_update(room_id='GENERAL', msg_id=rchat.welcome_message_id, text=sorted_users)
        msg = f'{system_time()} - User list updated'
        return msg