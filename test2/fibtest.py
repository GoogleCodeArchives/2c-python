import time
import pprint

def fib6(x):
    if x==0 or x==1:
        return 1
    else:
        return fib6(x-2)+fib6(x-1)
    
def main():    
    beg = time.clock()
    print fib6(33)
    end = time.clock()
    return end - beg
print __name__
print fib6, fib6.__code__
print fib6.__code__.co_c_function
print main
if __name__ == '__main__':
   d1 = main()
   import _c_fibtest
   d2 = _c_fibtest.main()
   print 'koef', d1 / d2
