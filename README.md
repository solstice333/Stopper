# StopLosser

## Description
stop loss calculator

## Usage
```
{ StopLosser } master » python3 stoplosser.py -h
usage: stoplosser.py [-h] -s SUPPORT -p HIGH_PRICE [-i INCR_DELTA]
                     [-n NUMSTOPS]

stop loss calculator to calculate multiple stops

optional arguments:
  -h, --help            show this help message and exit
  -s SUPPORT, --support SUPPORT
                        support price
  -p HIGH_PRICE, --high-price HIGH_PRICE
                        price of the security
  -i INCR_DELTA, --incr-delta INCR_DELTA
                        percentage between stops (defaults to 1.0 i.e. 1%)
  -n NUMSTOPS, --numstops NUMSTOPS
                        number of stops to be calculated starting from the
                        support

```
