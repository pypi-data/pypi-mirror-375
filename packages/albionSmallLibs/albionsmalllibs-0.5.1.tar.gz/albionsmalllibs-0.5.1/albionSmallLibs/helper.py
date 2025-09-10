def getStatFromBattle(battleJson: dict, guildName = 'O M B R A'):
    team1 = set()
    team2 = set()
    killsTeam1 = 0
    killsTeam2 = 0
    for kill in battleJson:
        victim = kill['Victim']
        killer = kill['Killer']
        if killer['GuildName'] == guildName:
            team1Kill = True
            team1.add(killer['Name'])
            team2.add(victim['Name'])
            killsTeam1 += 1
        elif victim['GuildName'] == guildName:
            team1Kill = False
            team2.add(killer['Name'])
            team1.add(victim['Name'])
            killsTeam2 += 1
        else:
            continue

        participants = kill['Participants']
        groupMembers = kill['GroupMembers']
        for party in [participants, groupMembers]:
            for member in party:
                if team1Kill:
                    team1.add(member['Name'])
                else:
                    team2.add(member['Name'])
                    
        #print("victim:", victim['Name'], victim['GuildName'], victim['AverageItemPower'], victim['Equipment']['MainHand']['Type'])
        #print("killer:", killer['Name'], killer['GuildName'], killer['AverageItemPower'], killer['Equipment']['MainHand']['Type'])
        
    return (team1, team2), (killsTeam1, killsTeam2)