import argparse
import math
import collections.abc as abc
from collections import namedtuple
import json
import sys

PercToPrice = namedtuple('PercToPrice', ['percent', 'price'])

class Stopper(abc.Sequence):
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

   def _gen_stoplist(self, fixed):
      stoplist = []
      perc = self._perc_to_support() if fixed else self._perc_to_support_ceil()

      for i in range(0, self._numstops):
         stoplist.append(
            PercToPrice(
               perc, 
               self._trunc_two_dec_places(
                  self._highprice - perc*self._highprice)))
         perc -= self._perc_to_dec(self._incrdelta)
      return stoplist

   @classmethod
   def get_stopper_within_support_range(
      cls, support_range, highprice, numstops, fixed):
      delta = 0.0
      support_low = min(support_range)
      support_high = max(support_range)
      prev_calc = cls(support_low, highprice, delta, numstops, fixed)
      calc = prev_calc

      while True:
         if calc[-1].price > support_high:
            calc = prev_calc
            break
         prev_calc = calc
         delta += 0.1
         calc = cls(support_low, highprice, delta, numstops, fixed)
      return calc

   def __init__(self, support, highprice, incrdelta, numstops, fixed=False):
      self._support = support
      self._highprice = highprice
      self._incrdelta = incrdelta
      self._numstops = numstops if numstops > 0 \
         else int(
            self._dec_to_perc(self._perc_to_support_ceil())/self._incrdelta)
      self._stoplist = self._gen_stoplist(fixed)

   def __getitem__(self, idx):
      return self._stoplist[idx]

   def __len__(self):
      return len(self._stoplist)

   def __repr__(self):
      return "Stopper({}, {}, {}, {})".format(
         self._support, self._highprice, self._incrdelta, self._numstops)

   @property
   def json(self):
      return json.dumps({
         'Stop Losses Percent to Price': self._stoplist,
         'IncrDelta percent': self._incrdelta }, sort_keys=True)

def main():
   """stop loss calculator tests

   >>> sl = Stopper(49.34, 55.30, 5.00, 3)
   >>> sl.json
   '{"IncrDelta percent": 5.0, "Stop Losses Percent to Price": [[0.11, 49.21], [0.06, 51.98], [0.009999999999999995, 54.74]]}'

   >>> sl = Stopper(49.34, 55.30, 1.00, 3)
   >>> sl.json
   '{"IncrDelta percent": 1.0, "Stop Losses Percent to Price": [[0.11, 49.21], [0.1, 49.77], [0.09000000000000001, 50.32]]}'

   >>> sl = Stopper(49.34, 55.30, 0.5, Stopper.MAXNUMSTOP)
   >>> sl.json
   '{"IncrDelta percent": 0.5, "Stop Losses Percent to Price": [[0.11, 49.21], [0.105, 49.49], [0.09999999999999999, 49.77], [0.09499999999999999, 50.04], [0.08999999999999998, 50.32], [0.08499999999999998, 50.59], [0.07999999999999997, 50.87], [0.07499999999999997, 51.15], [0.06999999999999997, 51.42], [0.06499999999999996, 51.7], [0.05999999999999996, 51.98], [0.054999999999999966, 52.25], [0.04999999999999997, 52.53], [0.04499999999999997, 52.81], [0.03999999999999997, 53.08], [0.034999999999999976, 53.36], [0.029999999999999975, 53.64], [0.024999999999999974, 53.91], [0.019999999999999973, 54.19], [0.014999999999999972, 54.47], [0.00999999999999997, 54.74], [0.004999999999999971, 55.02]]}'

   >>> sl = Stopper(49.34, 55.30, 1.0, Stopper.MAXNUMSTOP)
   >>> sl.json
   '{"IncrDelta percent": 1.0, "Stop Losses Percent to Price": [[0.11, 49.21], [0.1, 49.77], [0.09000000000000001, 50.32], [0.08000000000000002, 50.87], [0.07000000000000002, 51.42], [0.06000000000000002, 51.98], [0.05000000000000002, 52.53], [0.040000000000000015, 53.08], [0.030000000000000013, 53.64], [0.02000000000000001, 54.19], [0.01000000000000001, 54.74]]}'

   >>> sl = Stopper(51.26, 55.30, 1.0, 4, True)
   >>> sl.json
   '{"IncrDelta percent": 1.0, "Stop Losses Percent to Price": [[0.07305605786618444, 51.26], [0.06305605786618444, 51.81], [0.05305605786618444, 52.36], [0.04305605786618444, 52.91]]}'

   >>> sl = Stopper.get_stopper_within_support_range((46.5, 48.321), 50, 4, True)
   >>> sl.json
   '{"IncrDelta percent": 1.2, "Stop Losses Percent to Price": [[0.07, 46.5], [0.05800000000000001, 47.1], [0.04600000000000001, 47.7], [0.034000000000000016, 48.3]]}'
   """

   parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      description="stop loss calculator to calculate multiple stops. " +
         "Examples:\n\n" +
         "$ python {} -s 49.34 -p 55.30 -i 5.00 -n 3\n".format(sys.argv[0]) +
         "$ python {} -s 49.34 -p 55.30 -n 3\n".format(sys.argv[0]) +
         "$ python {} -s 49.34 -p 55.30 -i 0.5\n".format(sys.argv[0]) +
         "$ python {} -s 49.34 -p 55.30\n".format(sys.argv[0]) +
         "$ python {} -s 51.26 -p 55.30 -n 4 -f\n".format(sys.argv[0]) +
         "$ python3 {} -s 46.5 48.321 -p 50 -n 4 -f\n".format(sys.argv[0]))
   parser.add_argument('-s', '--support', type=float, nargs='+', required=True,
      help="support price(s) as floating point value(s)." +
         " This may be two values specifying a range, for example " +
         "-s 46.5 48.321. If specifying a range, -i cannot be used since " +
         "range semantics will automatically adjust -i to the optimal value. " +
         "Range semantics is the default. If only one value for -s is given, " +
         "that value is used as the min and max of the range")
   parser.add_argument('-p', '--high-price', type=float, required=True,
      help="price of the security as a floating point value")
   parser.add_argument('-i', '--incr-delta', type=float,
      help="percentage between stops as a floating point value." +
         " This overrides range semantics specified in -s")
   parser.add_argument('-n', '--numstops', type=int, 
      default=Stopper.MAXNUMSTOP, 
      help="number of stops (as an int) to be calculated starting " +
         "from the support")
   parser.add_argument('-f', '--fixed', action='store_true',
      help="don't perform a ceiling on the support percentage")

   args = parser.parse_args()
   args.support = min(args.support), max(args.support)

   if args.incr_delta is not None:
      calc = Stopper(
         args.support[0], args.high_price, args.incr_delta, 
         args.numstops, args.fixed)
   elif args.numstops == Stopper.MAXNUMSTOP:
      calc = Stopper(
         args.support[0], args.high_price, 1.0, args.numstops, args.fixed)
   else:
      calc = Stopper.get_stopper_within_support_range(
         args.support, args.high_price, args.numstops, args.fixed)

   print(calc.json)


if __name__ == '__main__':
   main()
