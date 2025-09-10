from .player import Player
from collections import Counter
import pickle

class BattleStat: # Need to handle n team
    def __init__(self, battleJson: dict, guildName = 'O M B R A'):
        self.battle = battleJson
        self.equipments = {}
        self.team1 = set()
        self.team2 = set()
        self.killsTeam1 = 0
        self.killsTeam2 = 0
        for kill in battleJson:
            victim = kill['Victim']
            killer = kill['Killer']
            if killer['GuildName'] == guildName:
                team1Kill = True
                self.addTeam(killer, 1)
                self.addTeam(victim, 2)
                self.killsTeam1 += 1
            elif victim['GuildName'] == guildName:
                team1Kill = False
                self.addTeam(killer, 2)
                self.addTeam(victim, 1)
                self.killsTeam2 += 1
            else:
                continue

            participants = [] #kill['Participants']
            groupMembers = kill['GroupMembers']
            for party in [participants, groupMembers]:
                for member in party:
                    if team1Kill:
                        self.addTeam(member, 1)
                    else:
                        self.addTeam(member, 2)
        
    def addTeam(self, playerData:dict, team:int):
        if playerData is None:
            return
        if team == 1:
            self.team1.add(playerData['Name'])
        else:
            self.team2.add(playerData['Name'])
        self.addEquipments(playerData)
    
        
    def addEquipments(self, playerData:dict):
        try:
            self.equipments[playerData['Name']] = Player(playerData['Name'], playerData['Equipment']['MainHand'], playerData['AverageItemPower'], playerData['GuildName'], playerData['AllianceName'] )
        except:
            print("Error in addEquipments: "+ str(playerData))
            
    def getGuildFromTeam(self, team:int):
        if team == 1:
            team = self.team1
        elif team == 2:
            team = self.team2
        else:
            raise Exception('Team must be 1 or 2')
            
        return Counter([self.equipments[player].guild for player in team])
    
    def getAllianceFromTeam(self, team:int):
        if team == 1:
            team = self.team1
        elif team == 2:
            team = self.team2
        else:
            raise Exception('Team must be 1 or 2')
            
        return Counter([self.equipments[player].alliance for player in team])
    
    def getDominationScore(self):
        if (self.killsTeam1 + self.killsTeam2) != 0:
            return self.killsTeam1 / (self.killsTeam1 + self.killsTeam2)

        return float('nan')
    
    def save(self, path):
        with open(path + 'battleData/'+str(self.battle[0] ['EventId'])+'.pkl', 'wb') as f:
            pickle.dump(self, f)
            
    def isValid(self):
        return len(self.team1) >0 and len(self.team2) >0
