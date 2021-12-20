"""
Option class
"""

import datetime
import math
import numpy as np
from scipy import stats as sts
from utils.descriptors import RealNumber, FutureDate


class Option:
    """
    A class for stock option handling. Determines price and greeks.
    """
    _LAZY_ATTR = ["_BS_price", "_MC_price", "_theta", "_gamma", "_delta", "_vega", "_rho"]
    price = RealNumber(min_value=0, sterilize_attr=_LAZY_ATTR)
    strike = RealNumber(min_value=0, sterilize_attr=_LAZY_ATTR)
    volatility = RealNumber(min_value=0, sterilize_attr=_LAZY_ATTR)
    dividend_yield = RealNumber(min_value=0, sterilize_attr=_LAZY_ATTR)
    risk_free_rate = RealNumber(sterilize_attr=_LAZY_ATTR)
    maturity = FutureDate(sterilize_attr=_LAZY_ATTR)

    def __init__(self, price, strike, volatility, risk_free_rate, maturity, dividend_yield=0):
        """

        Args:
            price (float or int): the underlying stock price
            strike (float or int): the contractual strike price
            dividend_yield (float or int): the expected dividend yield of the underlying (annualized)
            volatility (float or int): the underlying stock volatility (annualized)
            risk_free_rate (float or int): current risk-free-rate (annualized)
            maturity (str or datetime.datetime or datetime.date): maturity of the option
        """
        self.price = price
        self.strike = strike
        self.dividend_yield = dividend_yield
        self.volatility = volatility
        self.risk_free_rate = risk_free_rate
        self.maturity = maturity
        for attr in type(self)._LAZY_ATTR:
            setattr(self, attr, None)

    def __repr__(self):
        return f"Option(maturity={self.maturity}, strike={self.strike})"

    def __str__(self):
        return "OptionObject"

    def black_scholes_price(self):
        """
        Calculate the Black-Scholes price for the option.

        Returns:
            tuple: call and put option prices
        """
        if self._BS_price is None:
            t, d1, d2 = self._get_param()
            c = self.price * math.exp(-t * self.dividend_yield) * sts.norm.cdf(d1) - \
                self.strike * math.exp(- self.risk_free_rate * t) * sts.norm.cdf(d2)
            p = self.strike * math.exp(- self.risk_free_rate * t) * sts.norm.cdf(-d2) - \
                self.price * math.exp(-t * self.dividend_yield) * sts.norm.cdf(-d1)
            self._BS_price = (c, p)
        return self._BS_price

    def monte_carlo_price(self, n=1_000_000, seed=42):
        """
        Calculate the option price using Monte Carlo simulation
        Args:
            n (int): number of simulations
            seed (int): optional, seed for reproducibility

        Returns:
            tuple: call and put option prices
        """
        if self._MC_price is None:
            np.random.seed(seed)
            t = (self.maturity - datetime.date.today()).days / 360
            p_sim = np.random.lognormal(
                math.log(self.price) + (self.risk_free_rate - self.dividend_yield - 0.5 * self.volatility ** 2) * t,
                math.sqrt(t) * self.volatility, n)
            c = np.mean(np.where(p_sim > self.strike, p_sim - self.strike, 0)) * math.exp(-t * self.risk_free_rate)
            p = np.mean(np.where(p_sim < self.strike, self.strike - p_sim, 0)) * math.exp(-t * self.risk_free_rate)
            self._MC_price = (c, p)
        return self._MC_price

    def theta(self):
        """
        Calculates the option price derivative with respect to the time to maturity
        Returns:
            tuple: theta call option and theta put option
        """
        if self._theta is None:
            t, d1, d2 = self._get_param()
            theta_c = -(self.price * sts.norm.pdf(d1) * self.volatility * math.exp(-t * self.dividend_yield)) / (
                    2 * math.sqrt(t)) + self.dividend_yield * self.price * sts.norm.cdf(d1) * math.exp(
                -self.dividend_yield * t) - self.risk_free_rate * self.strike * math.exp(
                -self.risk_free_rate * t) * sts.norm.cdf(d2)
            theta_p = -(self.price * sts.norm.pdf(d1) * self.volatility * math.exp(-t * self.dividend_yield)) / (
                    2 * math.sqrt(t)) - self.dividend_yield * self.price * sts.norm.cdf(-d1) * math.exp(
                -self.dividend_yield * t) + self.risk_free_rate * self.strike * math.exp(
                -self.risk_free_rate * t) * sts.norm.cdf(-d2)
            self._theta = (theta_c, theta_p)
        return self._theta

    def gamma(self):
        """
        Calculates the option price second derivative with respect to the underlying price (gamma)
        Returns:
            tuple: gamma call option and gamma put option
        """
        if self._gamma is None:
            t, d1, _ = self._get_param()
            gamma = (sts.norm.pdf(d1) * math.exp(-self.dividend_yield * t)) / (
                    self.price * self.volatility * math.sqrt(t))
            self._gamma = (gamma, gamma)
        return self._gamma

    def rho(self):
        """
        Calculates the option price derivative with respect to the risk-free rate (rho)
        Returns:
            tuple: rho call option and rho put option
        """
        if self._rho is None:
            t, d1, d2 = self._get_param()
            self._rho = (self.strike * t * math.exp(-self.risk_free_rate * t) * sts.norm.cdf(d2),
                         -self.strike * t * math.exp(-self.risk_free_rate * t) * sts.norm.cdf(-d2))
        return self._rho

    def delta(self):
        """
        Calculates the option price derivative with respect to the underlying price (delta)
        Returns:
            tuple: delta call option and delta put option
        """
        if self._delta is None:
            t, d1, _ = self._get_param()
            self._delta = (math.exp(-t * self.dividend_yield) * sts.norm.cdf(d1),
                           math.exp(-t * self.dividend_yield) * (sts.norm.cdf(d1) - 1))
        return self._delta

    def vega(self):
        """
        Calculates the option price derivative with respect to the underlying volatility (vega)
        Returns:
            tuple: vega call option and vega put option
        """
        if self._vega is None:
            t, d1, _ = self._get_param()
            vega = self.price * math.sqrt(t) * sts.norm.pdf(d1) * math.exp(-self.dividend_yield * t)
            self._vega = vega, vega
        return self._vega

    def greeks(self):
        """
        Returns:
            tuple: return all the greeks
        """
        greeks = (self.delta(), self.gamma(), self.theta(), self.vega(), self.rho())
        return [(round(g[0], 4), round(g[1], 4)) for g in greeks]

    def _get_param(self):
        """
        Auxiliary function. Do not access directly.
        Returns:
            tuple: t, d1, d2
        """
        t = (self.maturity - datetime.date.today()).days / 360
        d1 = (math.log(self.price / self.strike) + (
                self.risk_free_rate - self.dividend_yield + 0.5 * self.volatility ** 2) * t) / (
                     self.volatility * math.sqrt(t))
        d2 = d1 - self.volatility * math.sqrt(t)
        return t, d1, d2

# TODO: implement greeks calculation
