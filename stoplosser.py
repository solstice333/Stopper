import argparse
import math
import collections.abc as abc
from collections import namedtuple
import json

PercToPrice = namedtuple('PercToPrice', ['percent', 'price'])

class StopLosser(abc.Sequence):
   MAXNUMSTOP = -1

   def _perc_to_support(self):
      return (self._highprice - self._support)/self._highprice

   def _perc_to_support_ceil(self):
      return self._perc_to_dec(
         math.ceil(self._dec_to_perc(self._perc_to_support())))

   def _places_mult(self, places):
      mult = 10;
      for i in range(1, places):
         mult*=10
      return mult

   def _dec_to_perc(self, val):
      return val*self._places_mult(2)

   def _perc_to_dec(self, val):
      return val/self._places_mult(2)

   def _trunc_dec_places(self, val, places):
      return int(val*self._places_mult(places))/self._places_mult(places)

   def _trunc_two_dec_places(self, val):
      return self._trunc_dec_places(val, 2)

   def _gen_stoplist(self):
      stoplist = []
      perc = self._perc_to_support_ceil()

      for i in range(0, self._numstops):
         stoplist.append(
            PercToPrice(
               perc, 
               self._trunc_two_dec_places(
                  self._highprice - perc*self._highprice)))
         perc -= self._perc_to_dec(self._incrdelta)
      return stoplist

   def __init__(self, support, highprice, incrdelta, numstops):
      self._support = support
      self._highprice = highprice
      self._incrdelta = incrdelta
      self._numstops = numstops if numstops > 0 \
         else int(
            self._dec_to_perc(self._perc_to_support_ceil())/self._incrdelta)
      self._stoplist = self._gen_stoplist()

   def __getitem__(self, idx):
      return self._stoplist[idx]

   def __len__(self):
      return len(self._stoplist)

   def __repr__(self):
      return "StopLosser({}, {}, {}, {})".format(
         self._support, self._highprice, self._incrdelta, self._numstops)

   @property
   def json(self):
      return json.dumps({'Stop Losses Percent to Price': self._stoplist})

def main():
   """stop loss calculator tests

   >>> sl = StopLosser(49.34, 55.30, 5.00, 3)
   >>> sl.json
   '{"Stop Losses Percent to Price": [[0.11, 49.21], [0.06, 51.98], [0.009999999999999995, 54.74]]}'

   >>> sl = StopLosser(49.34, 55.30, 1.00, 3)
   >>> sl.json
   '{"Stop Losses Percent to Price": [[0.11, 49.21], [0.1, 49.77], [0.09000000000000001, 50.32]]}'

   >>> sl = StopLosser(49.34, 55.30, 0.5, StopLosser.MAXNUMSTOP)
   >>> sl.json
   '{"Stop Losses Percent to Price": [[0.11, 49.21], [0.105, 49.49], [0.09999999999999999, 49.77], [0.09499999999999999, 50.04], [0.08999999999999998, 50.32], [0.08499999999999998, 50.59], [0.07999999999999997, 50.87], [0.07499999999999997, 51.15], [0.06999999999999997, 51.42], [0.06499999999999996, 51.7], [0.05999999999999996, 51.98], [0.054999999999999966, 52.25], [0.04999999999999997, 52.53], [0.04499999999999997, 52.81], [0.03999999999999997, 53.08], [0.034999999999999976, 53.36], [0.029999999999999975, 53.64], [0.024999999999999974, 53.91], [0.019999999999999973, 54.19], [0.014999999999999972, 54.47], [0.00999999999999997, 54.74], [0.004999999999999971, 55.02]]}'

   >>> sl = StopLosser(49.34, 55.30, 1.0, StopLosser.MAXNUMSTOP)
   >>> sl.json
   '{"Stop Losses Percent to Price": [[0.11, 49.21], [0.1, 49.77], [0.09000000000000001, 50.32], [0.08000000000000002, 50.87], [0.07000000000000002, 51.42], [0.06000000000000002, 51.98], [0.05000000000000002, 52.53], [0.040000000000000015, 53.08], [0.030000000000000013, 53.64], [0.02000000000000001, 54.19], [0.01000000000000001, 54.74]]}'
   """

   parser = argparse.ArgumentParser(
      description="stop loss calculator to calculate multiple stops")
   parser.add_argument('-s', '--support', type=float, required=True, 
      help="support price")
   parser.add_argument('-p', '--high-price', type=float, required=True,
      help="price of the security")
   parser.add_argument('-i', '--incr-delta', type=float, default=1.0,
      help="percentage between stops (defaults to 1.0 i.e. 1%%)")
   parser.add_argument('-n', '--numstops', type=int, 
      default=StopLosser.MAXNUMSTOP, 
      help="number of stops to be calculated starting from the support")

   args = parser.parse_args()

   stoploss_calc = StopLosser(
      args.support, args.high_price, args.incr_delta, args.numstops)
   print(stoploss_calc.json)


if __name__ == '__main__':
   main()
