# phs_poly

Example of gradient and Hessian calculation using RBF-FD.

To compile use,
```
gfortran -Wall -Og -o test_phs_poly phs_poly_approx.f90 test_phs_poly.f90 -llapack
```

Here's what the output should look like:

```txt
$ ./test_phs_poly

Testing 1
Grad (approx)    -0.000000   -0.000000
Grad (exact)      0.000000    0.000000
Hess (approx)    -0.000000   -0.000000    0.000000
Hess (exact)      0.000000    0.000000    0.000000

Testing x
Grad (approx)     1.000000   -0.000000
Grad (exact)      1.000000    0.000000
Hess (approx)    -0.000000    0.000000    0.000000
Hess (exact)      0.000000    0.000000    0.000000

Testing y
Grad (approx)    -0.000000    1.000000
Grad (exact)      0.000000    1.000000
Hess (approx)     0.000000   -0.000000    0.000000
Hess (exact)      0.000000    0.000000    0.000000

Testing x^2
Grad (approx)     0.862000    0.000000
Grad (exact)      0.862000    0.000000
Hess (approx)     2.000000   -0.000000    0.000000
Hess (exact)      2.000000    0.000000    0.000000

Testing y^2
Grad (approx)    -0.000000    1.074000
Grad (exact)      0.000000    1.074000
Hess (approx)     0.000000   -0.000000    2.000000
Hess (exact)      0.000000    0.000000    2.000000

Testing x*y
Grad (approx)     0.537000    0.431000
Grad (exact)      0.537000    0.431000
Hess (approx)     0.000000    1.000000    0.000000
Hess (exact)      0.000000    1.000000    0.000000

Testing general quad
Grad (approx)     6.734000    6.094000
Grad (exact)      6.734000    6.094000
Hess (approx)     6.000000    4.000000   10.000000
Hess (exact)      6.000000    4.000000   10.000000

Testing smooth function f(x,y) = sin(pi x)*cos(pi y)
Grad (approx)    -0.076949   -3.072093
Grad (exact)     -0.078364   -3.047367
Hess (approx)     1.121192   -2.065178    1.184418
Hess (exact)      1.117863   -2.108393    1.117863
```
