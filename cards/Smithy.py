from Card import Card, singleton
'''
    Action Card:
        +3 cards
'''
@singleton
class Smithy(Card):
    def __init__(self):
        Card.__init__(self, name='Smithy', cost=4, action=smith)

def smith(gameState):
    gameState = gameState.clone()
    gameState.pcards[gameState.turn].draw(3)
    return gameState
