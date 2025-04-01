"""
channels.py

This module defines the `Channel` class, which encapsulates information about a Discord channel.
Each channel object stores the channel ID and the channel name, and provides methods
to retrieve these details.

Author: GandalfTheSysAdmin
Date: 2024-08-31

Class:
    - Channel: Stores channel-specific information like channel ID and name.

Usage:
    - Import the `Channel` class in your script.
    - Create an instance of `Channel` by passing the channel ID and name as arguments.

Example:
    from channels import Channel
    channel = Channel('1166422305069600870', 'general')

License: MIT License
"""

CHANNELS = {
    'bluberry': '1166804125409890384',
    'bluberry-bog-testers': '1245854492235268198',
    'lemonhoko-genetix': '1152380117662838865',
    'blueberry-bx4-testers-aka-bluberry-xi': '1197604672366723142',
    'alien-hogdawg-testers': '1197605184625459210',
    'blueberry-bx5-testers': '1216941313228804096',
    'alien-blue-koffee': '1216946581891276800',
    'dibbs-testers': '1236719003771338805',
    'chem-dd-lines': '1165780172876816536',
    'holy-berry': '1165780396735217664',
    'dogon': '1168256032607310004',
    'dolly-patrone': '1168256087749828659',
    'headcheese-dd': '1168256247573778582',
    'glue-dd': '1168256286379483276',
    'berrywhite': '1168256346991366226',
    'hogdawg-v2': '1168256490067468378',
    'click-bait': '1168256575505436834',
    'q-cosmic-glue-dd': '1168256723430166580',
    'q-blue': '1214745566467067925',
    'big-sur-holy-weed': '1239608364070342737',
    'black-sur': '1239623276314099915',
    'larry-og': '1240424382195564585',
    'starfighter-f3': '1245854777666044107',
    'hogdawg-v1': '1168256890348523580',
    'blueberry-bx1': '1193654371237519390',
    'blueberry-bx2': '1193654420151746580',
    'blueberry-bx3': '1193654483460325417',
    'q-cherry': '1198736192465920040',
    'q-plum': '1198736236342792342',
    'white-sur': '1239623345482743859',
    'tropical-sur': '1239623393766510693',
    'purple-sur': '1239623442473246752',
    'road-dawg': '1168256528176574535',
    'cactus-breath': '1168256632384282624',
    'dragonsoul': '1168256674868785213',
    'alien-tahoe': '1197605228175618059',
    'alien-cookies': '1197605277993713716',
    
    # Breeder-specific channels
    'pacific-nw-roots': '1303027777221562440',
    'thunder-fudge-testing': '1300233673894920285',
    'twodog-seeds-joint': '1152744696305688647',
    'tds-farm-friend': '1195461323174187089',
    'blesscoast-shade-trees': '1152728582997684337',
    'blackbird-dirty-bird': '1152951045333450833',
    'terpfiend-test': '1281325179439415327',
    'groundbreaking-vortex': '1152947900767289404',
    'groundbreaking-seed-group': '1159230635915882607',
    'groundbreaking-breeder': '1165770434998968420',
    'groundbreaking-stardust': '1263578987981045954',
    # Add more channels here
}

class Channel:
    def __init__(self, channel_id, name):
        self.channel_id = channel_id
        self.name = name

    def __repr__(self):
        return f"Channel(name='{self.name}', channel_id='{self.channel_id}')"

    def get_channel_id(self):
        return self.channel_id

    def get_channel_name(self):
        return self.name

