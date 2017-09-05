def attackTerritories(p):       #random
    logging.info(p + " is attacking")  
    canAttackTerritories = set()
    for t in ownedTerritories:
        if territories[t].armies > 1 and any(territories[edge].player != p for edge in territories[t].edges):
            canAttackTerritories.add(t)
    while len(canAttackTerritories) > 0:                    # If we have a territory we can attack from
        if random.random() < 1:                          # Chance of attacking
            logging.info(p + " can attack from: " + str(canAttackTerritories))
            t = random.sample(canAttackTerritories,1)[0]    # Choose one territory to attack from, t
            possibleTargets = set()                         # Generate set of targets which can be attacked from t
            for edge in territories[t].edges:
                if territories[edge].player!= p:
                    possibleTargets.add(edge)
            logging.info("> Chosen: " + t)
            logging.info("Possible targets: " + str(possibleTargets))
            tDefend = random.sample(possibleTargets,1)[0]  # Choose attack target, tDefend
            logging.info("> Chosen: " + tDefend)
            diceAttack = random.randint(1,min(3,territories[t].armies - 1))     # Choose number of dice
            diceDefend = min(defendTerritory(p),territories[tDefend].armies)
            diceRollsAttack = []
            for i in range(diceAttack):
                diceRollsAttack.append(random.randint(1,6))
            diceRollsDefend = []
            for i in range(diceDefend):
                diceRollsDefend.append(random.randint(1,6))
            diceRollsAttack.sort(reverse = True)
            diceRollsDefend.sort(reverse = True)
            logging.info("Dice rolls: A" + str(diceRollsAttack) + "; D" + str(diceRollsDefend))
            lossesAttack = 0
            lossesDefend = 0
            compares = min(diceAttack,diceDefend)           # Number of dice to compare
            for i in range(compares):
                if diceRollsAttack[i] > diceRollsDefend[i]:
                    lossesDefend += 1
                else:
                    lossesAttack += 1
            logging.info("Losses: A" + str(lossesAttack) + "; D" + str(lossesDefend))
            
            territories[t].armies -= lossesAttack
            territories[tDefend].armies -= lossesDefend
            
            if territories[tDefend].armies == 0:
                occupyingArmies = diceAttack
                #(add potential to move more...)
                territories[tDefend].armies += territories[t].armies - 1
                territories[tDefend].player = p
                territories[t].armies = 1
                logging.info(p + " has occupied " + tDefend)
            
            #if displayMap:            
            #    updateMap([p],[t],[tDefend],0)            
            
            canAttackTerritories = set()
            for t in ownedTerritories:
                if territories[t].armies > 1 and any(territories[edge].player != p for edge in territories[t].edges):
                    canAttackTerritories.add(t)
            
        else:  
            # If we have decided not to attack
            logging.info(p + " has decided to cease attacking")
            break
            
def defendTerritory(p):          #random
    if random.getrandbits(1) == 1:
        return 1
    else:
        return 2