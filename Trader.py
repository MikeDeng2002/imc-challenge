from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import jsonpickle
import numpy as np
import math

class Product:
    SQUID_INK = "SQUID_INK"
    RAINFOREST_Resin = "RAINFOREST_WOOD"
    KELP_SEED = "KELP_SEED"

PARAMS ={
    Product.SQUID_INK: {
        "take_width": 1,
        "clear_width": 0,
        "prevent_adverse": True,
        "adverse_volume": 15,
        "reversion_beta": -0.229,
        "disregard_edge": 1,
        "join_edge": 0,
        "default_edge": 1,
},
    Product.RAINFOREST_Resin: {
      "fair_value": 10000,
        "take_width": 1,
        "clear_width": 0,
        # for making
        "disregard_edge": 1,  # disregards orders for joining or pennying within this value from fair
        "join_edge": 2,  # joins orders within this edge
        "default_edge": 4,
        "soft_position_limit": 10,
},
    Product.KELP_SEED: {
        "take_width": 1,
        "clear_width": 0,
        "prevent_adverse": True,
        "adverse_volume": 15,
        "reversion_beta": -0.229,
        "disregard_edge": 1,
        "join_edge": 0,
        "default_edge": 1,
}
}

class Trader:
    def __init__(self, params=None):
        if params is None:
            params = PARAMS
        self.params = params

        self.LIMIT = {Product.AMETHYSTS: 20, Product.STARFRUIT: 20}
    def take_best_order(self, order_depth: OrderDepth, product: Product):
        pass
    def market_make(self, product: Product, state: TradingState):
        pass
    def clear_orders(self, product: Product, order_depth: OrderDepth, fair_value: int, clear_width: int, position: int, buy_order_volume: int, sell_order_volume: int):
        pass
    def make_position_orders(self, product: Product, order_depth: OrderDepth, fair_value: int, position: int, buy_order_volume: int, sell_order_volume: int, disregard_edge: int, join_edge: int, default_edge: int, is_buy: bool, soft_position_limit: int):
        pass
    def squid_ink_fair_value(self, order_depth: OrderDepth, traderObject) -> float:
        if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
            best_ask = min(order_depth.sell_orders.keys())
            best_bid = max(order_depth.buy_orders.keys())
            filtered_ask = [
                price
                for price in order_depth.sell_orders.keys()
                if abs(order_depth.sell_orders[price])
                >= self.params[Product.SQUID_INK]["adverse_volume"]
            ]
            filtered_bid = [
                price
                for price in order_depth.buy_orders.keys()
                if abs(order_depth.buy_orders[price])
                >= self.params[Product.SQUID_INK]["adverse_volume"]
            ]
            mm_ask = min(filtered_ask) if len(filtered_ask) > 0 else None
            mm_bid = max(filtered_bid) if len(filtered_bid) > 0 else None
            if mm_ask == None or mm_bid == None:
                if traderObject.get("squid_ink_last_price", None) == None:
                    mmmid_price = (best_ask + best_bid) / 2
                else:
                    mmmid_price = traderObject["squid_ink_last_price"]
            else:
                mmmid_price = (mm_ask + mm_bid) / 2

            if traderObject.get("squid_ink_last_price", None) != None:
                last_price = traderObject["squid_ink_last_price"]
                last_returns = (mmmid_price - last_price) / last_price
                pred_returns = (
                    last_returns * self.params[Product.SQUID_INK]["reversion_beta"]
                )
                fair = mmmid_price + (mmmid_price * pred_returns)
            else:
                fair = mmmid_price
            traderObject["squid_ink_last_price"] = mmmid_price
            return fair
        return None    
    def KELP_SEED_fair_value(self, order_depth: OrderDepth, traderObject: Trader):
        if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
            best_ask = min(order_depth.sell_orders.keys())
            best_bid = max(order_depth.buy_orders.keys())
            filtered_ask = [
                price
                for price in order_depth.sell_orders.keys()
                if abs(order_depth.sell_orders[price])
                >= self.params[Product.KELP_SEED]["adverse_volume"]
            ]
            filtered_bid = [
                price
                for price in order_depth.buy_orders.keys()
                if abs(order_depth.buy_orders[price])
                >= self.params[Product.KELP_SEED]["adverse_volume"]
            ]
            mm_ask = min(filtered_ask) if len(filtered_ask) > 0 else None
            mm_bid = max(filtered_bid) if len(filtered_bid) > 0 else None
            if mm_ask == None or mm_bid == None:
                if traderObject.get("kelp_seed_last_price", None) == None:
                    mmmid_price = (best_ask + best_bid) / 2
                else:
                   mmmid_price = traderObject["kelp_seed_last_price"]
            else:
                mmmid_price = (mm_ask + mm_bid) / 2

            if traderObject.get("kelp_seed_last_price", None) != None:
                last_price = traderObject["kelp_seed_last_price"]
                last_returns = (mmmid_price - last_price) / last_price
                pred_returns = (
                    last_returns * self.params[Product.KELP_SEED]["reversion_beta"]
                )
                fair = mmmid_price + (mmmid_price * pred_returns)
            else:
                fair = mmmid_price
            traderObject["kelp_seed_last_price"] = mmmid_price
            return fair
        return None
    def take_orders(self, product: Product, order_depth: OrderDepth, fair_value: int, take_width: int, position: int):
        pass
    def clear_orders(self, product: Product, order_depth: OrderDepth, fair_value: int, clear_width: int, position: int, buy_order_volume: int, sell_order_volume: int):
        pass
    def make_orders(self, product: Product, order_depth: OrderDepth, fair_value: int, position: int, buy_order_volume: int, sell_order_volume: int, disregard_edge: int, join_edge: int, default_edge: int, is_buy: bool, soft_position_limit: int):
        pass
    def run(self, state: TradingState):
        traderObject = {}
        if state.traderData != None and state.traderData != "":
            traderObject = jsonpickle.decode(state.traderData)

        result = {}

        if Product.SQUID_INK in self.params and Product.SQUID_INK in state.order_depths:
            squid_ink_position = (
                state.position[Product.SQUID_INK]
                if Product.SQUID_INK in state.position
                else 0
            )
            amethyst_take_orders, buy_order_volume, sell_order_volume = (
                self.take_orders(
                    Product.SQUID_INK,
                    state.order_depths[Product.SQUID_INK],
                    self.params[Product.SQUID_INK]["fair_value"],
                    self.params[Product.SQUID_INK]["take_width"],
                    squid_ink_position,
                )
            )
            amethyst_clear_orders, buy_order_volume, sell_order_volume = (
                self.clear_orders(
                    Product.SQUID_INK,
                    state.order_depths[Product.SQUID_INK],
                    self.params[Product.SQUID_INK]["fair_value"],
                    self.params[Product.SQUID_INK]["clear_width"],
                    squid_ink_position,
                    buy_order_volume,
                    sell_order_volume,
                )
            )
            amethyst_make_orders, _, _ = self.make_orders(
                Product.SQUID_INK,
                state.order_depths[Product.SQUID_INK],
                self.params[Product.SQUID_INK]["fair_value"],
                squid_ink_position,
                buy_order_volume,
                sell_order_volume,
                self.params[Product.SQUID_INK]["disregard_edge"],
                self.params[Product.SQUID_INK]["join_edge"],
                self.params[Product.SQUID_INK]["default_edge"],
                True,
                self.params[Product.SQUID_INK]["soft_position_limit"],
            )
            result[Product.SQUID_INK] = (
                squid_ink_take_orders + squid_ink_clear_orders + squid_ink_make_orders
            )

        if Product.STARFRUIT in self.params and Product.STARFRUIT in state.order_depths:
            starfruit_position = (
                state.position[Product.STARFRUIT]
                if Product.STARFRUIT in state.position
                else 0
            )
            starfruit_fair_value = self.starfruit_fair_value(
                state.order_depths[Product.STARFRUIT], traderObject
            )
            starfruit_take_orders, buy_order_volume, sell_order_volume = (
                self.take_orders(
                    Product.STARFRUIT,
                    state.order_depths[Product.STARFRUIT],
                    starfruit_fair_value,
                    self.params[Product.STARFRUIT]["take_width"],
                    starfruit_position,
                    self.params[Product.STARFRUIT]["prevent_adverse"],
                    self.params[Product.STARFRUIT]["adverse_volume"],
                )
            )
            starfruit_clear_orders, buy_order_volume, sell_order_volume = (
                self.clear_orders(
                    Product.STARFRUIT,
                    state.order_depths[Product.STARFRUIT],
                    starfruit_fair_value,
                    self.params[Product.STARFRUIT]["clear_width"],
                    starfruit_position,
                    buy_order_volume,
                    sell_order_volume,
                )
            )
            starfruit_make_orders, _, _ = self.make_orders(
                Product.STARFRUIT,
                state.order_depths[Product.STARFRUIT],
                starfruit_fair_value,
                starfruit_position,
                buy_order_volume,
                sell_order_volume,
                self.params[Product.STARFRUIT]["disregard_edge"],
                self.params[Product.STARFRUIT]["join_edge"],
                self.params[Product.STARFRUIT]["default_edge"],
            )
            result[Product.STARFRUIT] = (
                starfruit_take_orders + starfruit_clear_orders + starfruit_make_orders
            )

        conversions = 1
        traderData = jsonpickle.encode(traderObject)

        return result, conversions, traderData
