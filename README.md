# oTree-Implementation-of-Journal-Replication---JEBO---Cheap-Talk-Messages-in-Experimental-Auctions

- 该实验由买家和卖家组成，要么2个卖家5个买家，要么5个卖家2个买家。
## 1 卖家：
    - 所卖的产品质量有高有低，但是对其他买家和卖家不可见。
    - 高质量产品生成的概率为0.25或者0.50，
    - 所有卖家同时销售自己的商品，即同时拍卖多个产品。
    - All auctions have a reservation price r, which is either exogenously fixed (F setting) or set by sellers (NF setting)，即保留价是内生的还是外生的
        - In F settings, the reservation price, r, is exogenously set at level vL/2 for all sellers.
        - In NF settings, the sellers observe cheap-talk messages of all other sellers and simultaneously set their reservation prices.
## 2 买家：
    - 收益计算
        - Buyers have unit demand and value low-quality products as vL, and high-quality products as vH.
        - The interpretation is that there is an outside venue (e.g., an offline store) where a product with known low quality can be purchased at the price of vL, and a product with known high quality can be purchased at the price of vH.
        - Thus, for example, if a buyer wins a low-quality object and pays price b, his gain, given the outside option, is exactly vL − b
## 3 拍卖方式有4种
    - first-price auction (FPA)：最高价者赢得商品并支付竞价，其他人不需要支付自己的竞价
    - second-price auction (SPA)：最高价者赢得商品并支付第二高的竞价，其他人不需要支付自己的竞价
    - sealed-bid double auction (DA)：the highest bidder wins the object only if their bid is higher than the seller’s ask price. In this case, the highest bidder pays the average of their own bid and the seller’s ask price （e.g.,p1 = (b1 + s1 )/2）. 除此之外，其他人不需要支付自己的竞价
    - all-pay auction (APA)：最高价者赢得商品并支付竞价。In APA, all bidders pay their bids regardless of whether they win or not.
## 4 流程：
    - ①Sellers observe q as well as the quality of their own products, vL or vH, ②and are asked to choose one of two cheap-talk messages: “I sell a low-quality product,” which we denote as mL, or “I sell a high-quality product,” which we denote as mH.
        - ***Notes：***
            - The chosen messages are public information.
            - In F settings, the reservation price, r, is exogenously set at level vL/2 for all sellers.
            - In NF settings, the sellers observe cheap-talk messages of all other sellers and simultaneously set their reservation prices.
    - ③Buyers observe q, sellers’ messages, and reservation prices.
    - ④Buyers can either quit and earn zero payoff or choose a seller whose auction they would like to join.
    - ⑤Participating buyers are informed about how many other bidders have joined the same auction and decide how much to bid.
    - ⑥In the double-auction treatments, the sellers also observe the number of bidders who participate in their auction and, based on this information, submit their ask prices. Ask prices and buyers’ bids are submitted simultaneously.
    - ⑦The round ends with buyers and sellers observing auction outcomes.
        - Sellers observe the number of bidders joining their auction, their bids, the winning bids, and the profits they earned.
        - Buyers observe all submitted bids in their auction, the true quality of the product, and their profits.
