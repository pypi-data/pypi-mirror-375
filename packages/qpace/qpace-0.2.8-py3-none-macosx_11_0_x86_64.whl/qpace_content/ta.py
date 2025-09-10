
  
from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from datetime import datetime
from qpace import Ctx, Backtest
from qpace_content import _lib
  
  


def accdist(ctx: Ctx, ) -> List[float]:
    """
Total money flowing in and out (Accumulation/Distribution)

`accdist() -> float`
    """
    return _lib.Incr_fn_accdist_30a368(ctx=ctx, ).collect()

class AccdistLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Accdist:
    """
Total money flowing in and out (Accumulation/Distribution)

`accdist() -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_accdist_30a368(ctx, )
        self.locals = AccdistLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    



def cum(ctx: Ctx, src: List[float], ) -> List[float]:
    """
Adds up the values so far (running total)

`cum(series<float> src) -> float`
    """
    return _lib.Incr_fn_cum_6094fe(ctx=ctx, ).collect(_3195_src=src)

class CumLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Cum:
    """
Adds up the values so far (running total)

`cum(series<float> src) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cum_6094fe(ctx, )
        self.locals = CumLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_3195_src=src)
    



def change(ctx: Ctx, src: List[float], ) -> List[float]:
    """
How much it moved from the previous bar

`change(series<float> src) -> series<float>`
    """
    return _lib.Incr_fn_change_18046d(ctx=ctx, ).collect(_3197_src=src)

class ChangeLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Change:
    """
How much it moved from the previous bar

`change(series<float> src) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_change_18046d(ctx, )
        self.locals = ChangeLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_3197_src=src)
    



def barssince(ctx: Ctx, condition: List[bool], ) -> List[int]:
    """
Number of bars since something happened

`barssince(series<bool> condition) -> int`
    """
    return _lib.Incr_fn_barssince_065aba(ctx=ctx, ).collect(_3199_condition=condition)

class BarssinceLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Barssince:
    """
Number of bars since something happened

`barssince(series<bool> condition) -> int`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_barssince_065aba(ctx, )
        self.locals = BarssinceLocals(self.inner)

    def next(self, condition: bool) -> Optional[int]:
        return self.inner.next(_3199_condition=condition)
    



def roc(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Speed of change over given bars

`roc(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_roc_3f2044(ctx=ctx, ).collect(_3201_src=src, _3202_length=length)

class RocLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Roc:
    """
Speed of change over given bars

`roc(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_roc_3f2044(ctx, )
        self.locals = RocLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3201_src=src, _3202_length=length)
    



def crossover(ctx: Ctx, source1: List[float], source2: List[float], ) -> List[bool]:
    """
When line1 moves above line2

`crossover(series<float> source1, series<float> source2) -> bool`
    """
    return _lib.Incr_fn_crossover_1b249d(ctx=ctx, ).collect(_3204_source1=source1, _3205_source2=source2)

class CrossoverLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Crossover:
    """
When line1 moves above line2

`crossover(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_crossover_1b249d(ctx, )
        self.locals = CrossoverLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_3204_source1=source1, _3205_source2=source2)
    



def crossunder(ctx: Ctx, source1: List[float], source2: List[float], ) -> List[bool]:
    """
When line1 drops below line2

`crossunder(series<float> source1, series<float> source2) -> bool`
    """
    return _lib.Incr_fn_crossunder_2164c6(ctx=ctx, ).collect(_3207_source1=source1, _3208_source2=source2)

class CrossunderLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Crossunder:
    """
When line1 drops below line2

`crossunder(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_crossunder_2164c6(ctx, )
        self.locals = CrossunderLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_3207_source1=source1, _3208_source2=source2)
    



def cross(ctx: Ctx, source1: List[float], source2: List[float], ) -> List[bool]:
    """
When two lines meet

`cross(series<float> source1, series<float> source2) -> bool`
    """
    return _lib.Incr_fn_cross_a5eb8d(ctx=ctx, ).collect(_3210_source1=source1, _3211_source2=source2)

class CrossLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Cross:
    """
When two lines meet

`cross(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cross_a5eb8d(ctx, )
        self.locals = CrossLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_3210_source1=source1, _3211_source2=source2)
    



def highestbars(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[int]:
    """
Bar index with highest value in period

`highestbars(series<float> src, int length = 14) -> int`
    """
    return _lib.Incr_fn_highestbars_54ee73(ctx=ctx, ).collect(_3213_src=src, _3214_length=length)

class HighestbarsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Highestbars:
    """
Bar index with highest value in period

`highestbars(series<float> src, int length = 14) -> int`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_highestbars_54ee73(ctx, )
        self.locals = HighestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[int]:
        return self.inner.next(_3213_src=src, _3214_length=length)
    



def lowestbars(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[int]:
    """
Bar index with lowest value in period

`lowestbars(series<float> src, int length = 14) -> int`
    """
    return _lib.Incr_fn_lowestbars_7de329(ctx=ctx, ).collect(_3216_src=src, _3217_length=length)

class LowestbarsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Lowestbars:
    """
Bar index with lowest value in period

`lowestbars(series<float> src, int length = 14) -> int`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lowestbars_7de329(ctx, )
        self.locals = LowestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[int]:
        return self.inner.next(_3216_src=src, _3217_length=length)
    



def highest(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Highest value in period

`highest(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_highest_008035(ctx=ctx, ).collect(_3219_src=src, _3220_length=length)

class HighestLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Highest:
    """
Highest value in period

`highest(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_highest_008035(ctx, )
        self.locals = HighestLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3219_src=src, _3220_length=length)
    



def lowest(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Lowest value in period

`lowest(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_lowest_742de3(ctx=ctx, ).collect(_3222_src=src, _3223_length=length)

class LowestLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Lowest:
    """
Lowest value in period

`lowest(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lowest_742de3(ctx, )
        self.locals = LowestLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3222_src=src, _3223_length=length)
    



def swma(ctx: Ctx, src: List[float], ) -> List[float]:
    """
Smoothed weighted moving average line

`swma(series<float> src) -> float`
    """
    return _lib.Incr_fn_swma_816d6f(ctx=ctx, ).collect(_3225_src=src)

class SwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Swma:
    """
Smoothed weighted moving average line

`swma(series<float> src) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_swma_816d6f(ctx, )
        self.locals = SwmaLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_3225_src=src)
    



def sma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Simple moving average (plain average)

`sma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_sma_7a7f3d(ctx=ctx, ).collect(_3227_src=src, _3228_length=length)

class SmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Sma:
    """
Simple moving average (plain average)

`sma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_sma_7a7f3d(ctx, )
        self.locals = SmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3227_src=src, _3228_length=length)
    



def ema(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Exponential moving average (reacts faster)

`ema(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_ema_517fb6(ctx=ctx, ).collect(_3230_src=src, _3231_length=length)

class EmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Ema:
    """
Exponential moving average (reacts faster)

`ema(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ema_517fb6(ctx, )
        self.locals = EmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3230_src=src, _3231_length=length)
    



def rma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
RMA used inside RSI

`rma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_rma_925847(ctx=ctx, ).collect(_3233_src=src, _3234_length=length)

class RmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Rma:
    """
RMA used inside RSI

`rma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_rma_925847(ctx, )
        self.locals = RmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3233_src=src, _3234_length=length)
    



def wma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Weighted moving average (recent bars matter more)

`wma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_wma_bfa520(ctx=ctx, ).collect(_3236_src=src, _3237_length=length)

class WmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Wma:
    """
Weighted moving average (recent bars matter more)

`wma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_wma_bfa520(ctx, )
        self.locals = WmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3236_src=src, _3237_length=length)
    



def lwma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Linear weighted moving average

`lwma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_lwma_fb7f1a(ctx=ctx, ).collect(_3239_src=src, _3240_length=length)

class LwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Lwma:
    """
Linear weighted moving average

`lwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lwma_fb7f1a(ctx, )
        self.locals = LwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3239_src=src, _3240_length=length)
    



def hma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Hull moving average (smooth and fast)

`hma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_hma_73b5d5(ctx=ctx, ).collect(_3242_src=src, _3243_length=length)

class HmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Hma:
    """
Hull moving average (smooth and fast)

`hma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_hma_73b5d5(ctx, )
        self.locals = HmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3242_src=src, _3243_length=length)
    



def vwma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Volume‑weighted moving average

`vwma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_vwma_28655e(ctx=ctx, ).collect(_3245_src=src, _3246_length=length)

class VwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Vwma:
    """
Volume‑weighted moving average

`vwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_vwma_28655e(ctx, )
        self.locals = VwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3245_src=src, _3246_length=length)
    



def dev(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Standard deviation (how much it varies)

`dev(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_dev_8c0088(ctx=ctx, ).collect(_3248_src=src, _3249_length=length)

class DevLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Dev:
    """
Standard deviation (how much it varies)

`dev(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_dev_8c0088(ctx, )
        self.locals = DevLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3248_src=src, _3249_length=length)
    



def tr(ctx: Ctx, handle_na: Optional[bool] = None, ) -> List[float]:
    """
True range (how much price moved in bar)

`tr(bool handle_na = true) -> series<float>`
    """
    return _lib.Incr_fn_tr_ec84ca(ctx=ctx, ).collect(_3251_handle_na=handle_na)

class TrLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Tr:
    """
True range (how much price moved in bar)

`tr(bool handle_na = true) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_tr_ec84ca(ctx, )
        self.locals = TrLocals(self.inner)

    def next(self, handle_na: Optional[bool] = None) -> Optional[float]:
        return self.inner.next(_3251_handle_na=handle_na)
    



def atr(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Average true range (typical move size)

`atr(int length = 14) -> float`
    """
    return _lib.Incr_fn_atr_2bbd4f(ctx=ctx, ).collect(_3253_length=length)

class AtrLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Atr:
    """
Average true range (typical move size)

`atr(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_atr_2bbd4f(ctx, )
        self.locals = AtrLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3253_length=length)
    



def rsi(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Relative Strength Index (momentum strength)

`rsi(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_rsi_8db613(ctx=ctx, ).collect(_3255_src=src, _3256_length=length)

class RsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Rsi:
    """
Relative Strength Index (momentum strength)

`rsi(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_rsi_8db613(ctx, )
        self.locals = RsiLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3255_src=src, _3256_length=length)
    



def cci(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Commodity Channel Index (price vs average)

`cci(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_cci_7ff883(ctx=ctx, ).collect(_3258_src=src, _3259_length=length)

class CciLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Cci:
    """
Commodity Channel Index (price vs average)

`cci(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cci_7ff883(ctx, )
        self.locals = CciLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3258_src=src, _3259_length=length)
    



def stdev(ctx: Ctx, src: List[float], length: int, biased: Optional[bool] = None, ) -> List[float]:
    """
Standard deviation over period

`stdev(series<float> src, int length, bool biased = true) -> float`
    """
    return _lib.Incr_fn_stdev_a7779d(ctx=ctx, ).collect(_3261_src=src, _3262_length=length, _3263_biased=biased)

class StdevLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Stdev:
    """
Standard deviation over period

`stdev(series<float> src, int length, bool biased = true) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_stdev_a7779d(ctx, )
        self.locals = StdevLocals(self.inner)

    def next(self, src: float, length: int, biased: Optional[bool] = None) -> Optional[float]:
        return self.inner.next(_3261_src=src, _3262_length=length, _3263_biased=biased)
    



def aroon(ctx: Ctx, length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Aroon indicator (time since highs/lows)

`aroon(int length = 14) -> [float, float]`
    """
    return _lib.Incr_fn_aroon_18cd66(ctx=ctx, ).collect(_3265_length=length)

class AroonLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Aroon:
    """
Aroon indicator (time since highs/lows)

`aroon(int length = 14) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_aroon_18cd66(ctx, )
        self.locals = AroonLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_3265_length=length)
    



def supertrend(ctx: Ctx, src: List[float], factor: float, atr_period: int, ) -> Tuple[float, int]:
    """
Supertrend line for direction

`supertrend(series<float> src, float factor, int atr_period) -> [float, int]`
    """
    return _lib.Incr_fn_supertrend_19a394(ctx=ctx, ).collect(_3267_src=src, _3268_factor=factor, _3269_atr_period=atr_period)

class SupertrendLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Supertrend:
    """
Supertrend line for direction

`supertrend(series<float> src, float factor, int atr_period) -> [float, int]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_supertrend_19a394(ctx, )
        self.locals = SupertrendLocals(self.inner)

    def next(self, src: float, factor: float, atr_period: int) -> Optional[Tuple[float, int]]:
        return self.inner.next(_3267_src=src, _3268_factor=factor, _3269_atr_period=atr_period)
    



def awesome_oscillator(ctx: Ctx, src: List[float], slow_length: Optional[int] = None, fast_length: Optional[int] = None, ) -> List[float]:
    """
Awesome Oscillator (momentum)

`awesome_oscillator(series<float> src, int slow_length = 5, int fast_length = 34) -> float`
    """
    return _lib.Incr_fn_awesome_oscillator_d66da6(ctx=ctx, ).collect(_3271_src=src, _3272_slow_length=slow_length, _3273_fast_length=fast_length)

class AwesomeOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class AwesomeOscillator:
    """
Awesome Oscillator (momentum)

`awesome_oscillator(series<float> src, int slow_length = 5, int fast_length = 34) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_awesome_oscillator_d66da6(ctx, )
        self.locals = AwesomeOscillatorLocals(self.inner)

    def next(self, src: float, slow_length: Optional[int] = None, fast_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3271_src=src, _3272_slow_length=slow_length, _3273_fast_length=fast_length)
    



def balance_of_power(ctx: Ctx, ) -> List[float]:
    """
Balance of power between buyers and sellers

`balance_of_power() -> float`
    """
    return _lib.Incr_fn_balance_of_power_4c514f(ctx=ctx, ).collect()

class BalanceOfPowerLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class BalanceOfPower:
    """
Balance of power between buyers and sellers

`balance_of_power() -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_balance_of_power_4c514f(ctx, )
        self.locals = BalanceOfPowerLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    



def bollinger_bands_pct_b(ctx: Ctx, src: List[float], length: Optional[int] = None, mult: Optional[float] = None, ) -> List[float]:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    return _lib.Incr_fn_bollinger_bands_pct_b_1b6aec(ctx=ctx, ).collect(_3278_src=src, _3279_length=length, _3280_mult=mult)

class BollingerBandsPctBLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBandsPctB:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_pct_b_1b6aec(ctx, )
        self.locals = BollingerBandsPctBLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None, mult: Optional[float] = None) -> Optional[float]:
        return self.inner.next(_3278_src=src, _3279_length=length, _3280_mult=mult)
    



def bollinger_bands_width(ctx: Ctx, src: List[float], length: Optional[int] = None, mult: Optional[float] = None, ) -> List[float]:
    """
Band width – how wide Bollinger Bands are

`bollinger_bands_width(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    return _lib.Incr_fn_bollinger_bands_width_cd1d99(ctx=ctx, ).collect(_3287_src=src, _3288_length=length, _3289_mult=mult)

class BollingerBandsWidthLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBandsWidth:
    """
Band width – how wide Bollinger Bands are

`bollinger_bands_width(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_width_cd1d99(ctx, )
        self.locals = BollingerBandsWidthLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None, mult: Optional[float] = None) -> Optional[float]:
        return self.inner.next(_3287_src=src, _3288_length=length, _3289_mult=mult)
    



def bollinger_bands(ctx: Ctx, src: List[float], length: Optional[int] = None, mult: Optional[float] = None, ) -> Tuple[float, float]:
    """
Gives upper and lower Bollinger Bands

`bollinger_bands(series<float> src, int length = 20, float mult = 2.0) -> [float, float]`
    """
    return _lib.Incr_fn_bollinger_bands_549c8d(ctx=ctx, ).collect(_3296_src=src, _3297_length=length, _3298_mult=mult)

class BollingerBandsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBands:
    """
Gives upper and lower Bollinger Bands

`bollinger_bands(series<float> src, int length = 20, float mult = 2.0) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_549c8d(ctx, )
        self.locals = BollingerBandsLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None, mult: Optional[float] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_3296_src=src, _3297_length=length, _3298_mult=mult)
    



def chaikin_money_flow(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """
    return _lib.Incr_fn_chaikin_money_flow_78f53a(ctx=ctx, ).collect(_3304_length=length)

class ChaikinMoneyFlowLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def cumVol(self) -> float:
        return self.__inner._3305_cumVol()
  
      

class ChaikinMoneyFlow:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_chaikin_money_flow_78f53a(ctx, )
        self.locals = ChaikinMoneyFlowLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3304_length=length)
    



def chande_kroll_stop(ctx: Ctx, atr_length: Optional[int] = None, atr_coeff: Optional[float] = None, stop_length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Chande‑Kroll stop lines

`chande_kroll_stop(int atr_length = 10, float atr_coeff = 1.0, int stop_length = 9) -> [float, float]`
    """
    return _lib.Incr_fn_chande_kroll_stop_5d8ef7(ctx=ctx, ).collect(_3309_atr_length=atr_length, _3310_atr_coeff=atr_coeff, _3311_stop_length=stop_length)

class ChandeKrollStopLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ChandeKrollStop:
    """
Chande‑Kroll stop lines

`chande_kroll_stop(int atr_length = 10, float atr_coeff = 1.0, int stop_length = 9) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_chande_kroll_stop_5d8ef7(ctx, )
        self.locals = ChandeKrollStopLocals(self.inner)

    def next(self, atr_length: Optional[int] = None, atr_coeff: Optional[float] = None, stop_length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_3309_atr_length=atr_length, _3310_atr_coeff=atr_coeff, _3311_stop_length=stop_length)
    



def choppiness_index(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Choppiness Index – tells if market is sideways or trending

`choppiness_index(int length = 14) -> float`
    """
    return _lib.Incr_fn_choppiness_index_673287(ctx=ctx, ).collect(_3320_length=length)

class ChoppinessIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ChoppinessIndex:
    """
Choppiness Index – tells if market is sideways or trending

`choppiness_index(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_choppiness_index_673287(ctx, )
        self.locals = ChoppinessIndexLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3320_length=length)
    



def connors_rsi(ctx: Ctx, src: List[float], rsi_length: Optional[int] = None, up_down_length: Optional[int] = None, roc_length: Optional[int] = None, ) -> List[float]:
    """
`connors_rsi(series<float> src, int rsi_length = 3, int up_down_length = 2, int roc_length = 100) -> float`
    """
    return _lib.Incr_fn_connors_rsi_96ca1e(ctx=ctx, ).collect(_3327_src=src, _3328_rsi_length=rsi_length, _3329_up_down_length=up_down_length, _3330_roc_length=roc_length)

class ConnorsRsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ConnorsRsi:
    """
`connors_rsi(series<float> src, int rsi_length = 3, int up_down_length = 2, int roc_length = 100) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_connors_rsi_96ca1e(ctx, )
        self.locals = ConnorsRsiLocals(self.inner)

    def next(self, src: float, rsi_length: Optional[int] = None, up_down_length: Optional[int] = None, roc_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3327_src=src, _3328_rsi_length=rsi_length, _3329_up_down_length=up_down_length, _3330_roc_length=roc_length)
    



def coppock_curve(ctx: Ctx, src: List[float], wma_length: Optional[int] = None, long_roc_length: Optional[int] = None, short_roc_length: Optional[int] = None, ) -> List[float]:
    """
Coppock Curve – long‑term momentum

`coppock_curve(series<float> src, int wma_length = 10, int long_roc_length = 14, int short_roc_length = 11) -> float`
    """
    return _lib.Incr_fn_coppock_curve_99ab27(ctx=ctx, ).collect(_3336_src=src, _3337_wma_length=wma_length, _3338_long_roc_length=long_roc_length, _3339_short_roc_length=short_roc_length)

class CoppockCurveLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class CoppockCurve:
    """
Coppock Curve – long‑term momentum

`coppock_curve(series<float> src, int wma_length = 10, int long_roc_length = 14, int short_roc_length = 11) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_coppock_curve_99ab27(ctx, )
        self.locals = CoppockCurveLocals(self.inner)

    def next(self, src: float, wma_length: Optional[int] = None, long_roc_length: Optional[int] = None, short_roc_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3336_src=src, _3337_wma_length=wma_length, _3338_long_roc_length=long_roc_length, _3339_short_roc_length=short_roc_length)
    



def donchian_channel(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> Tuple[float, float, float]:
    """
Donchian Channel highs/lows

`donchian_channel(series<float> src, int length = 20) -> [float, float, float]`
    """
    return _lib.Incr_fn_donchian_channel_f0dafb(ctx=ctx, ).collect(_3341_src=src, _3342_length=length)

class DonchianChannelLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class DonchianChannel:
    """
Donchian Channel highs/lows

`donchian_channel(series<float> src, int length = 20) -> [float, float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_donchian_channel_f0dafb(ctx, )
        self.locals = DonchianChannelLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[Tuple[float, float, float]]:
        return self.inner.next(_3341_src=src, _3342_length=length)
    



def macd(ctx: Ctx, src: List[float], short_length: Optional[int] = None, long_length: Optional[int] = None, ) -> List[float]:
    """
MACD line (fast trend vs slow)

`macd(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    return _lib.Incr_fn_macd_2a785d(ctx=ctx, ).collect(_3347_src=src, _3348_short_length=short_length, _3349_long_length=long_length)

class MacdLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Macd:
    """
MACD line (fast trend vs slow)

`macd(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_macd_2a785d(ctx, )
        self.locals = MacdLocals(self.inner)

    def next(self, src: float, short_length: Optional[int] = None, long_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3347_src=src, _3348_short_length=short_length, _3349_long_length=long_length)
    



def price_oscillator(ctx: Ctx, src: List[float], short_length: Optional[int] = None, long_length: Optional[int] = None, ) -> List[float]:
    """
Price oscillator in percent

`price_oscillator(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    return _lib.Incr_fn_price_oscillator_4e0e89(ctx=ctx, ).collect(_3352_src=src, _3353_short_length=short_length, _3354_long_length=long_length)

class PriceOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class PriceOscillator:
    """
Price oscillator in percent

`price_oscillator(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_price_oscillator_4e0e89(ctx, )
        self.locals = PriceOscillatorLocals(self.inner)

    def next(self, src: float, short_length: Optional[int] = None, long_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3352_src=src, _3353_short_length=short_length, _3354_long_length=long_length)
    



def relative_vigor_index(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Relative Vigor Index – strength of close vs range

`relative_vigor_index(int length = 14) -> float`
    """
    return _lib.Incr_fn_relative_vigor_index_c07b05(ctx=ctx, ).collect(_3359_length=length)

class RelativeVigorIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class RelativeVigorIndex:
    """
Relative Vigor Index – strength of close vs range

`relative_vigor_index(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_relative_vigor_index_c07b05(ctx, )
        self.locals = RelativeVigorIndexLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3359_length=length)
    



def relative_volatility_index(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Relative Volatility Index – like RSI but for volatility

`relative_volatility_index(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_relative_volatility_index_35470c(ctx=ctx, ).collect(_3361_src=src, _3362_length=length)

class RelativeVolatilityIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class RelativeVolatilityIndex:
    """
Relative Volatility Index – like RSI but for volatility

`relative_volatility_index(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_relative_volatility_index_35470c(ctx, )
        self.locals = RelativeVolatilityIndexLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3361_src=src, _3362_length=length)
    



def stochastic_rsi(ctx: Ctx, src: List[float], stoch_length: Optional[int] = None, rsi_length: Optional[int] = None, k: Optional[int] = None, d: Optional[int] = None, ) -> Tuple[float, float]:
    """
Stochastic RSI

`stochastic_rsi(series<float> src, int stoch_length = 14, int rsi_length = 14, int k = 3, int d = 3) -> [float, float]`
    """
    return _lib.Incr_fn_stochastic_rsi_cc8df0(ctx=ctx, ).collect(_3368_src=src, _3369_stoch_length=stoch_length, _3370_rsi_length=rsi_length, _3371_k=k, _3372_d=d)

class StochasticRsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class StochasticRsi:
    """
Stochastic RSI

`stochastic_rsi(series<float> src, int stoch_length = 14, int rsi_length = 14, int k = 3, int d = 3) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_stochastic_rsi_cc8df0(ctx, )
        self.locals = StochasticRsiLocals(self.inner)

    def next(self, src: float, stoch_length: Optional[int] = None, rsi_length: Optional[int] = None, k: Optional[int] = None, d: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_3368_src=src, _3369_stoch_length=stoch_length, _3370_rsi_length=rsi_length, _3371_k=k, _3372_d=d)
    



def ultimate_oscillator(ctx: Ctx, fast_length: Optional[int] = None, medium_length: Optional[int] = None, slow_length: Optional[int] = None, ) -> List[float]:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """
    return _lib.Incr_fn_ultimate_oscillator_14625d(ctx=ctx, ).collect(_3381_fast_length=fast_length, _3382_medium_length=medium_length, _3383_slow_length=slow_length)

class UltimateOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class UltimateOscillator:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ultimate_oscillator_14625d(ctx, )
        self.locals = UltimateOscillatorLocals(self.inner)

    def next(self, fast_length: Optional[int] = None, medium_length: Optional[int] = None, slow_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3381_fast_length=fast_length, _3382_medium_length=medium_length, _3383_slow_length=slow_length)
    



def volume_oscillator(ctx: Ctx, short_length: Optional[int] = None, long_length: Optional[int] = None, ) -> List[float]:
    """
Volume Oscillator – volume momentum

`volume_oscillator(int short_length = 5, int long_length = 10) -> float`
    """
    return _lib.Incr_fn_volume_oscillator_889e1d(ctx=ctx, ).collect(_3393_short_length=short_length, _3394_long_length=long_length)

class VolumeOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class VolumeOscillator:
    """
Volume Oscillator – volume momentum

`volume_oscillator(int short_length = 5, int long_length = 10) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_volume_oscillator_889e1d(ctx, )
        self.locals = VolumeOscillatorLocals(self.inner)

    def next(self, short_length: Optional[int] = None, long_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3393_short_length=short_length, _3394_long_length=long_length)
    



def vortex_indicator(ctx: Ctx, length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Vortex Indicator – shows trend direction

`vortex_indicator(int length = 14) -> [float, float]`
    """
    return _lib.Incr_fn_vortex_indicator_ae4b39(ctx=ctx, ).collect(_3399_length=length)

class VortexIndicatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class VortexIndicator:
    """
Vortex Indicator – shows trend direction

`vortex_indicator(int length = 14) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_vortex_indicator_ae4b39(ctx, )
        self.locals = VortexIndicatorLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_3399_length=length)
    



def williams_pct_r(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_williams_pct_r_791fac(ctx=ctx, ).collect(_3406_src=src, _3407_length=length)

class WilliamsPctRLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class WilliamsPctR:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_williams_pct_r_791fac(ctx, )
        self.locals = WilliamsPctRLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3406_src=src, _3407_length=length)
    



def advance_decline_ratio(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Advance/Decline Ratio (Bars)

`advance_decline_ratio(int length = 9) -> float`
    """
    return _lib.Incr_fn_advance_decline_ratio_097a74(ctx=ctx, ).collect(_3412_length=length)

class AdvanceDeclineRatioLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class AdvanceDeclineRatio:
    """
Advance/Decline Ratio (Bars)

`advance_decline_ratio(int length = 9) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_advance_decline_ratio_097a74(ctx, )
        self.locals = AdvanceDeclineRatioLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3412_length=length)
    



def detrended_price_oscillator(ctx: Ctx, length: Optional[int] = None, centered: Optional[bool] = None, ) -> List[float]:
    """
Detrended Price Oscillator (DPO)

`detrended_price_oscillator(int length = 21, bool centered = false) -> series<float>`
    """
    return _lib.Incr_fn_detrended_price_oscillator_f34999(ctx=ctx, ).collect(_3418_length=length, _3419_centered=centered)

class DetrendedPriceOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class DetrendedPriceOscillator:
    """
Detrended Price Oscillator (DPO)

`detrended_price_oscillator(int length = 21, bool centered = false) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_detrended_price_oscillator_f34999(ctx, )
        self.locals = DetrendedPriceOscillatorLocals(self.inner)

    def next(self, length: Optional[int] = None, centered: Optional[bool] = None) -> Optional[float]:
        return self.inner.next(_3418_length=length, _3419_centered=centered)
    



def bull_bear_power(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Bull Bear Power (BBP)

`bull_bear_power(int length = 13) -> series<float>`
    """
    return _lib.Incr_fn_bull_bear_power_41097f(ctx=ctx, ).collect(_3424_length=length)

class BullBearPowerLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BullBearPower:
    """
Bull Bear Power (BBP)

`bull_bear_power(int length = 13) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bull_bear_power_41097f(ctx, )
        self.locals = BullBearPowerLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3424_length=length)
    



def absolute_price_oscillator(ctx: Ctx, src: List[float], fast_length: Optional[int] = None, slow_length: Optional[int] = None, ) -> List[float]:
    """
Absolute Price Oscillator (APO)

`absolute_price_oscillator(series<float> src, int fast_length = 12, int slow_length = 26) -> float`
    """
    return _lib.Incr_fn_absolute_price_oscillator_beae09(ctx=ctx, ).collect(_3430_src=src, _3431_fast_length=fast_length, _3432_slow_length=slow_length)

class AbsolutePriceOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class AbsolutePriceOscillator:
    """
Absolute Price Oscillator (APO)

`absolute_price_oscillator(series<float> src, int fast_length = 12, int slow_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_absolute_price_oscillator_beae09(ctx, )
        self.locals = AbsolutePriceOscillatorLocals(self.inner)

    def next(self, src: float, fast_length: Optional[int] = None, slow_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3430_src=src, _3431_fast_length=fast_length, _3432_slow_length=slow_length)
    



def know_sure_thing(ctx: Ctx, src: List[float], roc_length1: Optional[int] = None, roc_length2: Optional[int] = None, roc_length3: Optional[int] = None, roc_length4: Optional[int] = None, sma_length1: Optional[int] = None, sma_length2: Optional[int] = None, sma_length3: Optional[int] = None, sma_length4: Optional[int] = None, sig_length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Know Sure Thing (KST)

`know_sure_thing(series<float> src, int roc_length1 = 10, int roc_length2 = 15, int roc_length3 = 20, int roc_length4 = 30, int sma_length1 = 10, int sma_length2 = 10, int sma_length3 = 10, int sma_length4 = 15, int sig_length = 9) -> [float, float]`
    """
    return _lib.Incr_fn_know_sure_thing_bbc3ef(ctx=ctx, ).collect(_3436_src=src, _3437_roc_length1=roc_length1, _3438_roc_length2=roc_length2, _3439_roc_length3=roc_length3, _3440_roc_length4=roc_length4, _3441_sma_length1=sma_length1, _3442_sma_length2=sma_length2, _3443_sma_length3=sma_length3, _3444_sma_length4=sma_length4, _3445_sig_length=sig_length)

class KnowSureThingLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class KnowSureThing:
    """
Know Sure Thing (KST)

`know_sure_thing(series<float> src, int roc_length1 = 10, int roc_length2 = 15, int roc_length3 = 20, int roc_length4 = 30, int sma_length1 = 10, int sma_length2 = 10, int sma_length3 = 10, int sma_length4 = 15, int sig_length = 9) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_know_sure_thing_bbc3ef(ctx, )
        self.locals = KnowSureThingLocals(self.inner)

    def next(self, src: float, roc_length1: Optional[int] = None, roc_length2: Optional[int] = None, roc_length3: Optional[int] = None, roc_length4: Optional[int] = None, sma_length1: Optional[int] = None, sma_length2: Optional[int] = None, sma_length3: Optional[int] = None, sma_length4: Optional[int] = None, sig_length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_3436_src=src, _3437_roc_length1=roc_length1, _3438_roc_length2=roc_length2, _3439_roc_length3=roc_length3, _3440_roc_length4=roc_length4, _3441_sma_length1=sma_length1, _3442_sma_length2=sma_length2, _3443_sma_length3=sma_length3, _3444_sma_length4=sma_length4, _3445_sig_length=sig_length)
    



def momentum(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Momentum (MOM)

`momentum(series<float> src, int length = 10) -> series<float>`
    """
    return _lib.Incr_fn_momentum_08a755(ctx=ctx, ).collect(_3453_src=src, _3454_length=length)

class MomentumLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Momentum:
    """
Momentum (MOM)

`momentum(series<float> src, int length = 10) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_momentum_08a755(ctx, )
        self.locals = MomentumLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3453_src=src, _3454_length=length)
    



def trix(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Trix

`trix(series<float> src, int length = 18) -> series<float>`
    """
    return _lib.Incr_fn_trix_8986ea(ctx=ctx, ).collect(_3456_src=src, _3457_length=length)

class TrixLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Trix:
    """
Trix

`trix(series<float> src, int length = 18) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_trix_8986ea(ctx, )
        self.locals = TrixLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3456_src=src, _3457_length=length)
    



def true_strength_index(ctx: Ctx, src: List[float], long_length: Optional[int] = None, short_length: Optional[int] = None, ) -> List[float]:
    """
True Strength Index (TSI)

`true_strength_index(series<float> src, int long_length = 25, int short_length = 13) -> float`
    """
    return _lib.Incr_fn_true_strength_index_4ae749(ctx=ctx, ).collect(_3459_src=src, _3460_long_length=long_length, _3461_short_length=short_length)

class TrueStrengthIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class TrueStrengthIndex:
    """
True Strength Index (TSI)

`true_strength_index(series<float> src, int long_length = 25, int short_length = 13) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_true_strength_index_4ae749(ctx, )
        self.locals = TrueStrengthIndexLocals(self.inner)

    def next(self, src: float, long_length: Optional[int] = None, short_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3459_src=src, _3460_long_length=long_length, _3461_short_length=short_length)
    



def dema(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Double Exponential Moving Average (DEMA)

`dema(series<float> src, int length = 9) -> float`
    """
    return _lib.Incr_fn_dema_563c5b(ctx=ctx, ).collect(_3467_src=src, _3468_length=length)

class DemaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Dema:
    """
Double Exponential Moving Average (DEMA)

`dema(series<float> src, int length = 9) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_dema_563c5b(ctx, )
        self.locals = DemaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3467_src=src, _3468_length=length)
    



def fwma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Fibonacci Weighted Moving Average (FWMA)

`fwma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_fwma_7bcc92(ctx=ctx, ).collect(_3477_src=src, _3478_length=length)

class FwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Fwma:
    """
Fibonacci Weighted Moving Average (FWMA)

`fwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_fwma_7bcc92(ctx, )
        self.locals = FwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3477_src=src, _3478_length=length)
    



def money_flow_index(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Money Flow Index (MFI)

`money_flow_index(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_money_flow_index_fbe185(ctx=ctx, ).collect(_3484_src=src, _3485_length=length)

class MoneyFlowIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class MoneyFlowIndex:
    """
Money Flow Index (MFI)

`money_flow_index(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_money_flow_index_fbe185(ctx, )
        self.locals = MoneyFlowIndexLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3484_src=src, _3485_length=length)
    



def ease_of_movement(ctx: Ctx, length: Optional[int] = None, divisor: Optional[int] = None, ) -> List[float]:
    """
Ease of Movement (EOM)

`ease_of_movement(int length = 14, int divisor = 10000) -> float`
    """
    return _lib.Incr_fn_ease_of_movement_ef68bd(ctx=ctx, ).collect(_3487_length=length, _3488_divisor=divisor)

class EaseOfMovementLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class EaseOfMovement:
    """
Ease of Movement (EOM)

`ease_of_movement(int length = 14, int divisor = 10000) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ease_of_movement_ef68bd(ctx, )
        self.locals = EaseOfMovementLocals(self.inner)

    def next(self, length: Optional[int] = None, divisor: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3487_length=length, _3488_divisor=divisor)
    



def elder_force_index(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Elder Force Index (EFI)

`elder_force_index(int length = 13) -> float`
    """
    return _lib.Incr_fn_elder_force_index_12b49d(ctx=ctx, ).collect(_3490_length=length)

class ElderForceIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ElderForceIndex:
    """
Elder Force Index (EFI)

`elder_force_index(int length = 13) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_elder_force_index_12b49d(ctx, )
        self.locals = ElderForceIndexLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3490_length=length)
    



def tema(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Tripple Exponential Moving Average (TEMA)

`tema(series<float> src, int length = 9) -> float`
    """
    return _lib.Incr_fn_tema_116f84(ctx=ctx, ).collect(_3492_src=src, _3493_length=length)

class TemaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Tema:
    """
Tripple Exponential Moving Average (TEMA)

`tema(series<float> src, int length = 9) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_tema_116f84(ctx, )
        self.locals = TemaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_3492_src=src, _3493_length=length)
    


class MainAlert(TypedDict):
    time: datetime
    bar_index: int
    title: Optional[str]
    message: Optional[str]

class MainResultLocals(TypedDict):

    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, ) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_744294(ctx=ctx, ).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_744294(ctx, )
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          