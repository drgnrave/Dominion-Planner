from Player import Player
from sys import stdin
from util.MDPBase import MarkovDecisionProcess
from cards import *
from engine.InputSets import InputSets
import GeneticDeck

class GUMDRP(Player):
    def __init__(self, stacks, params, cvparams):
        self._makingAction = False
        self.params = params
        self.cvparams = cvparams
        self.goalDeck = GeneticDeck.generateGoalDeck(stacks, stacks.keys(), params, reps = 1, deckSize = 17)
        self.miniDeck = GeneticDeck.generateMiniDeck(stacks, stacks.keys(), params, reps = 1)
        self.mdpDiscount = 1
    
    def evaluate(self, gameState):
        abcs = gameState.abcs[gameState.turn]
        total_coins = abcs['coins'] + sum([card.coins*gameState.pcards[0].hand[card] for card in gameState.pcards[0].hand])
        v = [0,0,0,0,0]
        v[0] = abcs['actions'] * len(list(InputSets.handCardSet(gameState, number=1, filtered = lambda c: (c.action != None))))
        v[1] = min(abcs['buys']*8, total_coins)
        v[2] = total_coins
        v[3] = sum([c.cost*n for c,n in gameState.pcards[gameState.turn].allCards().items()])
        v[4] = (gameState.pcards[gameState.turn].currInPlay.count + gameState.pcards[gameState.turn].hand.count)
        return sum([v[i]*self.params[i] for i in xrange(len(self.params))])
                
    def selectInput(self, inputs, gameState, actionSimulator=None, helpMessage=None):
        _makingAction = self._makingAction
        self._makingAction = False
        m = -1
        choice = None
        inputs = list(inputs)
        for i in inputs:
            temp = 0
            if actionSimulator != None:
                for x in xrange(3):
                    gs = actionSimulator(gameState, i)
                    temp += MarkovDecisionProcess(gs, self.evaluate, discount = self.mdpDiscount, cutOff = 0).run()[0]
            if temp > m:
                m = temp
                choice = tuple(i)
        if _makingAction:
            self._makingAction = True
#            if hasattr(choice, '__iter__'):
 #               print '(' + choice[0].name + ')',
  #          else:
   #             print '(' + str(choice) + ')',
        return choice
        '''
        _makingAction = self._makingAction
        self._makingAction = False
        inputs = list(inputs)
        if (not inputs) or (not actionSimulator):
            selectedInput = None
        else:
            inputs_value = ((sum((self.evaluate(actionSimulator(gameState, i)) for trial in xrange(5)))/5, i) for i in inputs) 
            selectedInput = max(inputs_value)[1]
        if _makingAction:
            self._makingAction = True
            if hasattr(selectedInput, '__iter__'):
                print '(' + selectedInput[0].name + ')',
            else:
                print '(' + str(selectedInput) + ')',
        return selectedInput
        '''    
    
    def playActionPhase(self, gameState):
        gameState = gameState.clone()
        while self.availableActions(gameState):
            choice = None
            v = self.evaluate(gameState)
            mdp = MarkovDecisionProcess(gameState, self.evaluate, discount = self.mdpDiscount, cutOff = 3).run()
            #if (mdp[0] > v):
            choice = mdp[1]
            if not choice:
                break
            else:
                choice = choice[0]
   #             print 'Play: ' + choice.name,
                gameState.pcards[gameState.turn].playFromHand(choice)
                gameState.abcs[gameState.turn]['actions'] -= 1
                self._makingAction = True
                gameState = choice.action(gameState)
                self._makingAction = False
    #            print '\n\t' + str(gameState.abcs[gameState.turn])
     #           print '\thand: ' + str(gameState.pcards[gameState.turn].hand)
        return gameState
        
    def playBuyPhase(self, gameState):
        gameState = gameState.clone()
        abcs = gameState.abcs[gameState.turn]
        coins = gameState.abcs[gameState.turn]['coins'] + self.totalTreasure(gameState)
        cards = gameState.pcards[gameState.turn] 
        while abcs['buys'] > 0:
            possibleBuys = self.availableBuys(gameState, coins)
            if not possibleBuys:
                break
            value_buys = ((self.valueCard(gameState, c), c) for c in possibleBuys)
            maxBuy = max(value_buys)
            if maxBuy[0][2] < 0:
                break;
            buy = maxBuy[1]
            gameState.stacks[buy] -= 1
            abcs['buys'] -= 1
            coins -= buy.cost
            gameState.pcards[gameState.turn].gain(buy)
        gameState.abcs[gameState.turn]['coins'] = coins
        return gameState
        
    def playDiscardPhase(self, gameState):
        gameState = gameState.clone()
        gameState.pcards[gameState.turn].discardPhase()
        return gameState
    
    def valueCard(self, gameState, card):
        if card in [Copper.Copper(), Estate.Estate()]:
            return (0,0,-1)
        cards = gameState.pcards[gameState.turn]
        
        if len(self.goalDeck - cards.allCards())==0:
            if card in [Province.Province()]:
                return (10000,0,0)
        if card in (self.goalDeck).keys():
            num_left = gameState.stacks[card]
            card_amount = (self.goalDeck - cards.allCards())[card]
            if card_amount == 0: card_amount = -100
            return (num_left*self.cvparams[0] + card_amount*self.cvparams[1]+ card.cost*self.cvparams[2], 0, 0)
        if card in (self.miniDeck).keys():
            num_left = gameState.stacks[card]
            card_amount = (self.miniDeck - cards.allCards())[card]
            if card_amount == 0: card_amount = -100
            return (0, num_left*self.cvparams[0] + card_amount*self.cvparams[1]+ card.cost*self.cvparams[2], 0)
        else:
            return (0,0,card.cost)
    
        '''
        towards_goal_deck = int(card in cards_to_buy)
        num_left = gameState.stacks[card]
        card_amount = cards_to_buy[card]
        in_goal_deck = towards_goal_deck*self.cvparams[0] + card_amount*self.cvparams[1]
        
        return card.cost*self.cvparams[2] + in_goal_deck 
        '''
        '''if card==Province.Province() and (gameState.abcs[gameState.turn]['coins']>=11):
            return 10000000
        if (card.victoryPoints or card==Copper.Copper() or (card==Silver.Silver() and gameState.pcards[0].allCards()[Silver.Silver()]>4)):
            return -2
        if card==Gold.Gold() and gameState.pcards[0].allCards()[Gold.Gold()]<gameState.pcards[0].allCards()[Market.Market()]:
            return 1000000
        if card==Laboratory.Laboratory():
            return 10000*gameState.stacks[card]
        if card.cost==5:
            return 10000*gameState.stacks[card]
        return self.params[0]*card.cost '''

