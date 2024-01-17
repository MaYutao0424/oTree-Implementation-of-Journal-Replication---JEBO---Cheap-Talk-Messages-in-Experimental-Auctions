from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):        
        yield Introduction
        import random
        random.seed(0)

        if self.player.role == 'SELLER 1' or self.player.role == 'SELLER 2':
            yield SellerMessage,dict(SellerMessage = random.randint(1,2))
            yield SellerReservation,dict(SellerReservationPrice = int(random.randint(C.RemainPriceLow,C.RemainPriceLow+300)))
            yield SellersResults

        if self.player.role != 'SELLER 1' and self.player.role != 'SELLER 2':
            RobotChoice = random.randint(1,2)
            yield BuyerDecision2Bid,dict(BuyerSellerChoice = RobotChoice)
            if RobotChoice == 1:
                yield G1Bid,dict(BuyerBid = int(random.randint(int(C.RemainPriceLow+300),int(C.RemainPriceLow+600))))
            else:
                yield G2Bid,dict(BuyerBid = int(random.randint(int(C.RemainPriceLow+300),int(C.RemainPriceLow+600))))
            yield BuyersResults
