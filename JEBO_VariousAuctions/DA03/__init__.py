from otree.api import *
from settings import SESSION_CONFIGS

doc = """
Your app description
"""

class C(BaseConstants):
    NAME_IN_URL = 'double_auction(SPA)'
    PLAYERS_PER_GROUP = 7
    NUM_ROUNDS = 2
    ENDOWMENT = 5000

    '''角色初始化'''
    # 对于每一组而言，组中id为1和2的为卖家其余为买家
    # 通过后续的group_randomly()将每位参与者在组中的id打乱实现角色随机分配
    Seller1_ROLE = 'SELLER 1'
    Seller2_ROLE = 'SELLER 2'
    Buyer1_ROLE = 'BUYER 1'
    Buyer2_ROLE = 'BUYER 2'
    Buyer3_ROLE = 'BUYER 3'
    Buyer4_ROLE = 'BUYER 4'
    Buyer5_ROLE = 'BUYER 5'
    Seller_Num = 2
    Buyer_Num = PLAYERS_PER_GROUP-Seller_Num
   
    '''商品初始化'''
    # 卖家商品为高质量的概率、高质量商品的价值、低质量商品的价值
    import random
    import numpy as np
    random.seed(0)
    HighQuality_p = 0.25
    LowQuality_v = int(round(np.random.normal(2000, 100)))
    HighQuality_v = int(round(random.uniform(2, 2.5),2)*LowQuality_v)
    RemainPriceLow = int(LowQuality_v/2)

class Subsession(BaseSubsession):
    final_payoff_round = models.IntegerField()

class Group(BaseGroup):
    bid_winner_id = models.IntegerField(initial=0)

class Player(BasePlayer):

    # 卖家相关字段，包括卖家选择发送的信息、商品质量和顺序(index为1或者2)
    SellerMessage = models.IntegerField(
        choices=[
            [1, 'I sell a HIGH-quality product.'],
            [2, 'I sell a LOW-quality product.'],
        ],
        widget=widgets.RadioSelectHorizontal,
        label= 'Decide which message you would like to send to the buyers in the market. You can choose either message, regardless of your product quality.',
        initial=0,
    )
    SellerProductQuality = models.StringField()
    SellerReservationPrice = models.IntegerField(min=C.RemainPriceLow,label=f'Now, decide your reservation price. Your reservation price should be at least <strong>{C.RemainPriceLow}</strong>.')
    SellerAskPrice = models.IntegerField()
    SellerDownResPrice = models.BooleanField(initial=False)

    # 买家相关字段，包括买家所选择的卖家、竞价
    BuyerSellerChoice = models.IntegerField(
        choices=[
            [1, "Bid for SELLER 1's product."],
            [2, "Bid for SELLER 2's product."],
            [3,'Do not bid.']
        ],
        widget=widgets.RadioSelectHorizontal,
        label= "Based on the given information, please decide whether you want to bid for any Seller's product, or do not want to bid at all:",
        initial= 0,
    )
    BuyerBid = models.IntegerField(initial=0)
    # 记录买家实际支付自身bid与卖家ask price的平均价格
    Actual_BuyerBid = models.IntegerField(initial=0)
    is_winner = models.BooleanField(initial=False)

    # 玩家共有字段：利润
    profit = models.IntegerField(initial=0)

'''参与者每轮加入的队伍、所扮演的角色是变化的'''
def creating_session(subsession: Subsession):
    subsession.group_randomly()
'''表单验证-卖家的Ask Price需要大于他之前所出示的保留价'''
def SellerAskPrice_error_message(player, value):
    if value < player.SellerReservationPrice:
        return f'Your ask price should be greater than or equal to the reservation price, <strong>{player.SellerReservationPrice}</strong>'

def BuyerBid_error_message(player, value):
    Seller1 = player.group.get_player_by_id(1)
    Seller2 = player.group.get_player_by_id(2)
    if player.BuyerSellerChoice == 1:
        if value < Seller1.SellerReservationPrice:
            return 'Your bid should be greater than or equal to the reservation price'
    elif player.BuyerSellerChoice == 2:
        if value < Seller2.SellerReservationPrice:
            return 'Your bid should be greater than or equal to the reservation price'    
# PAGES
class Introduction(Page):
    pass

class SellerMessage(Page):
    form_model = 'player'
    form_fields = ['SellerMessage']

    @staticmethod
    def is_displayed(player: Player):
        if player.role == 'SELLER 1' or player.role == 'SELLER 2':
            return True
    
    @staticmethod
    def vars_for_template(player: Player):
        import random
        player.SellerProductQuality = random.choices(['HIGH','LOW'], weights=[C.HighQuality_p,1-C.HighQuality_p], k=1).pop()

class SellerDecisionWaitPage(WaitPage):
    title_text = "Please wait for SELLERs to make a decision"
    body_text = "Please wait for SELLERs to make a decision"

class SellerReservation(Page):
    form_model = 'player'
    form_fields = ['SellerReservationPrice']

    @staticmethod
    def vars_for_template(player: Player):
        my_seller_id = player.id_in_group
        if my_seller_id == 1:
            another_seller = player.group.get_player_by_role('SELLER 2')
        else:
            another_seller = player.group.get_player_by_role('SELLER 1')
        return dict(
            another_seller=another_seller,
            SellerReservationPrice_MIN= C.LowQuality_v/2
        )

    @staticmethod
    def is_displayed(player: Player):
        if player.role == 'SELLER 1' or player.role == 'SELLER 2':
            return True

class BuyerDecision2Bid(Page):
    form_model = 'player'
    form_fields = ['BuyerSellerChoice']

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(
            SELLER1 = group.get_player_by_role('SELLER 1'),
            SELLER2 = group.get_player_by_role('SELLER 2')
        )
    
    @staticmethod
    def is_displayed(player: Player):
        if player.role != 'SELLER 1' and player.role != 'SELLER 2':
            return True

class BuyerDecisionWaitPage(WaitPage):
    title_text = "Please wait for BUYERs to make a decision"
    body_text = "Please wait for BUYERs to make a decision"

class G1Bid(Page):
    form_model = 'player'
    form_fields = ['BuyerBid']

    @staticmethod
    def vars_for_template(player: Player):
        all_players = player.group.get_players()
        G1_buyers = []
        for b in all_players:
            if b.BuyerSellerChoice == 1:
                G1_buyers.append(b)
        other_buyer_number = len(G1_buyers)-1
        seller_this_group = player.group.get_player_by_id(1)
        return dict(
            other_buyer_number = other_buyer_number,
            seller_this_group = seller_this_group
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.BuyerSellerChoice == 1

class G2Bid(Page):
    form_model = 'player'
    form_fields = ['BuyerBid']

    @staticmethod
    def vars_for_template(player: Player):
        all_players = player.group.get_players()
        G2_buyers = []
        for b in all_players:
            if b.BuyerSellerChoice == 2:
                G2_buyers.append(b)
        other_buyer_number = len(G2_buyers)-1
        seller_this_group = player.group.get_player_by_id(2)
        return dict(
            other_buyer_number = other_buyer_number,
            seller_this_group = seller_this_group
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.BuyerSellerChoice == 2

class G3Bid(Page):
    @staticmethod
    def vars_for_template(player: Player):
        Seller1 = player.group.get_player_by_id(1)
        Seller2 = player.group.get_player_by_id(2)
        #买家根据自己的选择，分配到g1(卖家1)、g2(卖家2)、g3(无卖家)
        all_players = player.group.get_players()
        group1_buyers_num = 0
        group2_buyers_num = 0
        group3_buyers_num = 0
        for b in all_players:
            if b.BuyerSellerChoice == 1:
                group1_buyers_num += 1
            elif b.BuyerSellerChoice == 2:
                group2_buyers_num += 1
            elif b.BuyerSellerChoice == 3:
                group3_buyers_num += 1

        total_buyers_num = C.Buyer_Num  

        return dict(
            SELLER1 = Seller1,
            SELLER2 = Seller2,
            group1_buyers_num = group1_buyers_num,
            group2_buyers_num = group2_buyers_num,
            total_buyers_num = total_buyers_num,
        )
    
    @staticmethod
    def is_displayed(player: Player):
        return player.BuyerSellerChoice == 3

class SellerAskPrice(Page):
    form_model = 'player'
    form_fields = ['SellerAskPrice']

    @staticmethod
    def vars_for_template(player: Player):
        all_players = player.group.get_players()
        buyers_this_group = []
        for b in all_players:
            if b.BuyerSellerChoice == player.id_in_group:
                buyers_this_group.append(b)
        return dict(
            my_seller_id = player.id_in_group,
            buyer_number = len(buyers_this_group),
        )

    @staticmethod
    def is_displayed(player: Player):
        if player.role == 'SELLER 1' or player.role == 'SELLER 2':
            return  True

class BidWaiting(WaitPage):
    title_text = "Please wait for BUYERs to make a decision"
    body_text = "Please wait for BUYERs to make a decision"

    @staticmethod
    def after_all_players_arrive(group: Group):
        # 先确定谁是赢家
        all_players = group.get_players()
        Seller1 = group.get_player_by_id(1)
        Seller2 = group.get_player_by_id(2)
        G1 = []
        G2 = []
        for b in all_players:
            if b.BuyerSellerChoice == 1:
                G1.append(b)
            elif b.BuyerSellerChoice == 2:
                G2.append(b)
            else:
                pass
        G1.sort(key=lambda b: b.BuyerBid,reverse=True)
        G2.sort(key=lambda b: b.BuyerBid,reverse=True)

        if len(G1)>0:
            if G1[0].BuyerBid >= Seller1.SellerAskPrice:
                G1[0].is_winner = True
                G1[0].Actual_BuyerBid = int((G1[0].BuyerBid+Seller1.SellerAskPrice)/2)
            else:
                Seller1.SellerDownResPrice = True
        else:
            pass

        if len(G2)>0:
            if G2[0].BuyerBid >= Seller2.SellerAskPrice:
                G2[0].is_winner = True
                G2[0].Actual_BuyerBid = int((G2[0].BuyerBid+Seller2.SellerAskPrice)/2)
            else:
                Seller2.SellerDownResPrice = True
        else:
            pass

        # 计算收益

        for g1 in G1:
            if g1.is_winner:
                if Seller1.SellerProductQuality == 'HIGH':
                    g1.profit = C.HighQuality_v - g1.Actual_BuyerBid
                    Seller1.profit = g1.Actual_BuyerBid
                else:
                    g1.profit = C.LowQuality_v - g1.Actual_BuyerBid
                    Seller1.profit = g1.Actual_BuyerBid
            else:
                pass
        
        for g2 in G2:
            if g2.is_winner:
                if Seller2.SellerProductQuality == 'HIGH':
                    g2.profit = C.HighQuality_v - g2.Actual_BuyerBid
                    Seller2.profit = g2.Actual_BuyerBid
                else:
                    g2.profit = C.LowQuality_v - g2.Actual_BuyerBid
                    Seller2.profit = g2.Actual_BuyerBid
            else:
                pass

class BuyersResults(Page):

    @staticmethod
    def vars_for_template(player: Player):
        Seller1 = player.group.get_player_by_id(1)
        Seller2 = player.group.get_player_by_id(2)
        #买家根据自己的选择，分配到g1(卖家1)、g2(卖家2)、g3(无卖家)
        all_players = player.group.get_players()
        total_buyers_num = C.Buyer_Num 
        group1_buyers_num = 0
        group2_buyers_num = 0
        buyers_this_group = []
        for b in all_players:
            if b.BuyerSellerChoice == 1:
                group1_buyers_num += 1
            elif b.BuyerSellerChoice == 2:
                group2_buyers_num += 1
            else:
                pass
            if b.BuyerSellerChoice == player.BuyerSellerChoice:
                buyers_this_group.append(b)
        
        return dict(
            SELLER1 = Seller1,
            SELLER2 = Seller2,
            group1_buyers_num = group1_buyers_num,
            group2_buyers_num = group2_buyers_num,
            total_buyers_num = total_buyers_num,
            buyers_this_group = buyers_this_group,
        )

    @staticmethod
    def is_displayed(player: Player):
        if player.role != 'SELLER 1' and player.role != 'SELLER 2' and player.BuyerSellerChoice != 3:
            return True

class SellersResults(Page):
    @staticmethod
    def vars_for_template(player: Player):

        Seller1 = player.group.get_player_by_id(1)
        Seller2 = player.group.get_player_by_id(2)

        all_players = player.group.get_players()
        total_buyers_num =  C.Buyer_Num
        group1_buyers_num = 0
        group2_buyers_num = 0
        buyers_this_group = []
        for b in all_players:
            if b.BuyerSellerChoice == 1:
                group1_buyers_num += 1
            elif b.BuyerSellerChoice == 2:
                group2_buyers_num += 1
            else:
                pass
            if b.BuyerSellerChoice == player.id_in_group:
                buyers_this_group.append(b)

        winner_select = buyers_this_group.copy()
        winner_select.sort(key=lambda w: w.BuyerBid,reverse=True)
        if not winner_select:
            winnerId = 0
        else:
            winnerId = winner_select[0].id_in_group-2
        return dict(
            SELLER1 = Seller1,
            SELLER2 = Seller2,
            group1_buyers_num = group1_buyers_num,
            group2_buyers_num = group2_buyers_num,
            total_buyers_num = total_buyers_num,
            buyers_this_group = buyers_this_group,
            winnerId = winnerId
        )

    @staticmethod
    def is_displayed(player: Player):
        if player.role == 'SELLER 1' or player.role == 'SELLER 2':
            return  True

class RoundEndWaiting(WaitPage):
    wait_for_all_groups = True
    @staticmethod
    def after_all_players_arrive(subsession):
        import random
        random.seed(0)
        final_payoff_round = random.randint(1,C.NUM_ROUNDS)
        subsession.final_payoff_round = final_payoff_round

class FinalPage(Page):

    @staticmethod
    def vars_for_template(player: Player):
        player_in_seleced_round = player.in_round(player.subsession.final_payoff_round)
        player_in_seleced_round.profit = C.ENDOWMENT+player_in_seleced_round.profit
        return dict(
            player_in_seleced_round = player_in_seleced_round
        )


    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

page_sequence = [Introduction,SellerMessage,SellerDecisionWaitPage,SellerReservation,SellerDecisionWaitPage,BuyerDecision2Bid,BuyerDecisionWaitPage,G1Bid,G2Bid,SellerAskPrice,BidWaiting,BuyersResults,SellersResults,G3Bid,RoundEndWaiting,FinalPage]
