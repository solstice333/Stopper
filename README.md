# Stopper

## Description
stop loss calculator

## Usage
```
usage: stopper.py [-h] -s SUPPORT -p HIGH_PRICE [-i INCR_DELTA] [-n NUMSTOPS]
                  [-f]

stop loss calculator to calculate multiple stops. Examples:

$ python stopper.py -s 49.34 -p 55.30 -i 5.00 -n 3
$ python stopper.py -s 49.34 -p 55.30 -n 3
$ python stopper.py -s 49.34 -p 55.30 -i 0.5
$ python stopper.py -s 49.34 -p 55.30
$ python stopper.py -s 51.26 -p 55.30 -n 4 -f

optional arguments:
  -h, --help            show this help message and exit
  -s SUPPORT, --support SUPPORT
                        support price as a floating point value
  -p HIGH_PRICE, --high-price HIGH_PRICE
                        price of the security as a floating point value
  -i INCR_DELTA, --incr-delta INCR_DELTA
                        percentage between stops as a floating point value
                        (defaults to 1.0 i.e. 1%)
  -n NUMSTOPS, --numstops NUMSTOPS
                        number of stops (as an int) to be calculated starting
                        from the support
  -f, --fixed           don't perform a ceiling on the percentages

```

Use `python -m doctest -v stopper.py` to run tests
