from enum import Enum

HEAL_WEAPON =  ['NATURESTAFF', 'HOLYSTAFF', 'DIVINESTAFF', 'WILDSTAFF']
DPS_WEAPON = ['HALBERD', 'AXE', 'KNUCKLES', 'SWORD', 'CROSSBOW', 'DAGGER',
              'SPEAR', 'BOW' , 'GLACIALSTAFF', 'SCYTHE', 'INFERNOSTAFF',
              'FIRE', 'CLAYMORE','SCIMITAR', 'GLAIVE', 'HARPOON', 'RAPIER',
              'FROSTSTAFF','ICECRYSTAL', 'CLAWPAIR', 'DUALSICKLE', 'CLEAVER',
              'SHAPESHIFTER_SET1',  'SHAPESHIFTER_SET3', 'SHAPESHIFTER_AVALON', 
              'SHAPESHIFTER_HELL' ]
TANK_WEAPON = ['HAMMER', 'MACE', 'FLAIL', 'IRONCLADEDSTAFF', 'ROCKSTAFF', 'TRIDENT',
               'RAM', 'SHAPESHIFTER_KEEPER']
SUPPORT_WEAPON = ['COMBATSTAFF', 'ARCANE', 'CURSEDSTAFF', 'ENIGMATICSTAFF',
                  'DEMONICSTAFF', 'ENIGMATICORB','ICEGAUNTLETS',
                  'DOUBLEBLADEDSTAFF', 'QUARTERSTAFF', 'SHAPESHIFTER_SET2']

class Role(Enum):
    HEAL = 1
    DPS = 2
    TANK = 3
    SUPPORT = 4
    OTHER = 5
    

class Player:
    def __init__(self, name: str, weapon: dict, ip : float, guildName = None, allianceName = None):
        self.name = name
        self.ip = ip
        self.guild = guildName
        self.alliance = allianceName
        if weapon is None:
            self.weaponFullName = "None"
        else:
            self.weaponFullName = weapon['Type']
    
    
    def getType(self):
        weapon_name = self.getWeaponName()
        if any(weapon in weapon_name for weapon in HEAL_WEAPON):
            return Role.HEAL
        elif any(weapon in weapon_name for weapon in TANK_WEAPON):
            return Role.TANK
        elif any(weapon in weapon_name for weapon in DPS_WEAPON):
            return Role.DPS
        elif any(weapon in weapon_name for weapon in SUPPORT_WEAPON):
            return Role.SUPPORT
        else:
            return Role.OTHER

    def getWeaponName(self):
        splitStr = self.weaponFullName.split("_")
        if len(splitStr)>=3:
            weapon = splitStr[2].split('@')[0]
            if weapon == "SHAPESHIFTER":
                return "SHAPESHIFTER_"+ splitStr[3].split('@')[0]
            return weapon
        else:
            return self.weaponFullName



