from Card import Card, singleton
'''
    Action Card:
        Reveal cards from your deck until you reveal 2 Treasure cards.
        Put those Treasure cards into your hand and discard the other revealed
        cards.
'''
@singleton
class Adventurer(Card):
    def __init__():
        super(Card, self).__init__(self, name='Adventurer', cost=6,
                act=adventure, ctype='a')

def adventure(gameState):
    currentCards = gameState.pcards[gameState.turn]
    num = 2
    while num:
        card = currentCards.revealCard(keep=treasureCard)
        if 't' in card.ctype:
            num -= 1
    currentCards.revealCard(stop=True)

def treasureCard(card):
    return cards.coins > 0
