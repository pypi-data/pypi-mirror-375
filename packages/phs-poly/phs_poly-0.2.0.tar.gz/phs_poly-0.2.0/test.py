import numpy as np
import phs_poly  # your CPython extension module

def test_quadratic(name, x, y, coeffs, gx_exact, gy_exact, hxx_exact, hxy_exact, hyy_exact):
    if name == "1":
        f = np.ones_like(x)
    elif name == "x":
        f = x
    elif name == "y":
        f = y
    elif name == "x^2":
        f = x**2
    elif name == "y^2":
        f = y**2
    elif name == "x*y":
        f = x * y
    elif name == "general quad":
        f = 1 + 2*x - y + 3*x**2 + 4*x*y + 5*y**2
    else:
        raise ValueError(f"Unknown test case {name}")

    gx  = np.sum(coeffs[:,0] * f)
    gy  = np.sum(coeffs[:,1] * f)
    hxx = np.sum(coeffs[:,2] * f)
    hxy = np.sum(coeffs[:,3] * f)
    hyy = np.sum(coeffs[:,4] * f)

    print(f"\nTesting {name}")
    print(f"Grad (approx) {gx:12.6f} {gy:12.6f}")
    print(f"Grad (exact)  {gx_exact:12.6f} {gy_exact:12.6f}")
    print(f"Hess (approx) {hxx:12.6f} {hxy:12.6f} {hyy:12.6f}")
    print(f"Hess (exact)  {hxx_exact:12.6f} {hxy_exact:12.6f} {hyy_exact:12.6f}")


def test_smooth(x, y, coeffs, xc, yc):

    pi = np.pi
    f = np.sin(pi*x) * np.cos(pi*y)

    gx  = np.sum(coeffs[:,0] * f)
    gy  = np.sum(coeffs[:,1] * f)
    hxx = np.sum(coeffs[:,2] * f)
    hxy = np.sum(coeffs[:,3] * f)
    hyy = np.sum(coeffs[:,4] * f)

    gx_exact  = pi * np.cos(pi*xc) * np.cos(pi*yc)
    gy_exact  = -pi * np.sin(pi*xc) * np.sin(pi*yc)
    hxx_exact = -pi**2 * np.sin(pi*xc) * np.cos(pi*yc)
    hxy_exact = -pi**2 * np.cos(pi*xc) * np.sin(pi*yc)
    hyy_exact = -pi**2 * np.sin(pi*xc) * np.cos(pi*yc)

    print("\nTesting smooth function f(x,y) = sin(pi x)*cos(pi y)")
    print(f"Grad (approx) {gx:12.6f} {gy:12.6f}")
    print(f"Grad (exact)  {gx_exact:12.6f} {gy_exact:12.6f}")
    print(f"Hess (approx) {hxx:12.6f} {hxy:12.6f} {hyy:12.6f}")
    print(f"Hess (exact)  {hxx_exact:12.6f} {hxy_exact:12.6f} {hyy_exact:12.6f}")


def main():
    nx, ny = 5, 5
    n = nx * ny
    ldc = n + 6

    xc = 0.431
    yc = 0.537

    # grid points
    xv, yv = np.meshgrid(np.linspace(0,1,nx), np.linspace(0,1,ny), indexing="xy")
    x = xv.ravel()
    y = yv.ravel()

    coeffs = np.zeros((ldc, 5), dtype=np.float64,order='F')
    wrk = np.zeros((ldc, n+6), dtype=np.float64,order='F')
    iwrk = np.zeros(n+6, dtype=np.int32)

    ierr = phs_poly.phs3_poly2(n, x - xc, y - yc, coeffs, ldc, wrk, iwrk)
    if ierr != 0:
        raise RuntimeError(f"phs3_poly2 failed with ierr={ierr}")

    # Keep only the PHS weights
    coeffs = coeffs[0:n,:]

    # Quadratic tests
    test_quadratic("1",          x, y, coeffs, 0.0, 0.0, 0.0, 0.0, 0.0)
    test_quadratic("x",          x, y, coeffs, 1.0, 0.0, 0.0, 0.0, 0.0)
    test_quadratic("y",          x, y, coeffs, 0.0, 1.0, 0.0, 0.0, 0.0)
    test_quadratic("x^2",        x, y, coeffs, 2*xc, 0.0, 2.0, 0.0, 0.0)
    test_quadratic("y^2",        x, y, coeffs, 0.0, 2*yc, 0.0, 0.0, 2.0)
    test_quadratic("x*y",        x, y, coeffs, yc, xc, 0.0, 1.0, 0.0)

    # general quadratic
    test_quadratic("general quad", x, y, coeffs,
                   2.0 + 6*xc + 4*yc,
                  -1.0 + 4*xc + 10*yc,
                   6.0,
                   4.0,
                  10.0)

    # smooth function
    test_smooth(x, y, coeffs, xc, yc)


if __name__ == "__main__":
    main()
