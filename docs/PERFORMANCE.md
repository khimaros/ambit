# PERFORMANCE

## Overview

The hardware has some interesting performance considerations.

The hardware can receive a relatively high volume of writes, but as
soon as input is received, performance drops off precipitously.

Performance with input is lower by factor of ~2.5.

Each additional attached component also reduces write speed.

Topology may also play a role in performance. My hypothesis is
that increased *depth* of the topology reduces performance.

## Benchmarks

Constant SLIDER movement (8 components)

```
screen_string 22.001065731048584 45.45234363755248 per second
led 35.74591612815857 27.97522369869429 per second
configure_leds 41.08134436607361 6.08548731444287 per second
```

No input (8 components)

```
screen_string 14.842199087142944 67.37546061258874 per second
led 32.701507568359375 30.57962994242989 per second
configure_leds 37.949182987213135 6.587757108874696 per second
```

## Benchmarks (legacy)

No input (1 component, base only)

```
screen_string 0.30580759048461914 163.5015007991268 per second
led 0.6479833126068115 77.16248092694232 per second
configure_leds 0.6500790119171143 76.91372753682295 per second
```

No input (2 components)

```
screen_string 0.5950770378112793 84.02273457551361 per second
led 1.1165986061096191 44.77884866273188 per second
configure_leds 1.6022875308990479 31.20538544785708 per second
```

Continuous DIAL ROTATION input (2 components)

```
screen_string 1.7495856285095215 28.57819542253281 per second
led 2.2195706367492676 22.526879375746677 per second
configure_leds 2.9930288791656494 16.705485318918218 per second
```

No input (4 components)

```
screen_string 1.2214667797088623 40.93439201999218 per second
led 1.7843656539916992 28.021162528065897 per second
configure_leds 4.148374080657959 12.052914956037348 per second
```

No input (6 components)

```
screen_string 1.9131205081939697 26.13531128114933 per second
led 2.522559881210327 19.82113501940336 per second
configure_leds 8.794707298278809 5.68523753027976 per second
```

No input (8 components):

```
screen_string 2.8802568912506104 17.359562666748783 per second
led 3.575145959854126 13.985442989309481 per second
configure_leds 15.192654609680176 3.29106408883553 per second
```

Continuous SLIDER SET input (8 components):

```
screen_string 7.475589275360107 6.688435942408225 per second
led 8.045717716217041 6.214485986653425 per second
configure_leds 32.79039549827576 1.5248367468647699 per second
```
