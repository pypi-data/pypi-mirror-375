program test_phs_poly

    use phs_poly_approx

    implicit none

    integer, parameter :: wp = kind(1.0d0)
    integer :: nx, ny, n, ldc, ierr
    real(wp), allocatable :: x(:), y(:)
    real(wp), allocatable :: coeffs(:,:), wrk(:,:)
    integer, allocatable :: iwrk(:)
    real(wp) :: xc, yc
    integer :: i, j, k

    ! mesh size
    nx = 5
    ny = 5
    n  = nx * ny
    ldc = n + 10

    ! evaluation point
    xc = 0.431_wp
    yc = 0.537_wp

    ! allocate arrays
    allocate(x(n), y(n))
    allocate(coeffs(ldc,5), wrk(ldc,n+10))
    allocate(iwrk(n+10))

    ! fill coordinates on [0,1]x[0,1]
    i = 0
    do j = 0, ny-1
        do k = 0, nx-1
            i = i + 1
            x(i) = real(k,wp)/(nx-1)
            y(i) = real(j,wp)/(ny-1)
        end do
    end do

    ! Build weights
    !    N.b. coordinates are shifted into local coordinate system at stencil center
    call phs3_poly2(n,(x - xc),(y - yc),coeffs,ldc,wrk,iwrk,ierr)
    if (ierr /= 0) then
        print *, "phs3_poly2 failed with ierr=",ierr
        stop
    end if

    ! run tests
    call test_quadratic("1",          x, y, coeffs, 0._wp, 0._wp, 0._wp, 0._wp, 0._wp)
    call test_quadratic("x",          x, y, coeffs, 1._wp, 0._wp, 0._wp, 0._wp, 0._wp)
    call test_quadratic("y",          x, y, coeffs, 0._wp, 1._wp, 0._wp, 0._wp, 0._wp)
    call test_quadratic("x^2",        x, y, coeffs, 2*xc, 0._wp, 2._wp, 0._wp, 0._wp)
    call test_quadratic("y^2",        x, y, coeffs, 0._wp, 2*yc, 0._wp, 0._wp, 2._wp)
    call test_quadratic("x*y",        x, y, coeffs, yc, xc, 0._wp, 1._wp, 0._wp)

    ! general quadratic: f(x,y) = 1 + 2x - y + 3x^2 + 4xy + 5y^2
    call test_quadratic("general quad", x, y, coeffs, &
        2._wp + 6*xc + 4*yc, &  ! df/dx
       -1._wp + 4*xc + 10*yc, & ! df/dy
        6._wp, &                ! d²/dx²
        4._wp, &                ! d²/dxdy
       10._wp)                  ! d²/dy²

    ! smooth trigonometric function
    call test_smooth(x,y,coeffs,xc,yc)

contains

    subroutine test_quadratic(name,x,y,coeffs,gx_exact,gy_exact,hxx_exact,hxy_exact,hyy_exact)
        character(*), intent(in) :: name
        real(wp), intent(in) :: x(:), y(:)
        real(wp), intent(in) :: coeffs(:,:)
        real(wp), intent(in) :: gx_exact, gy_exact, hxx_exact, hxy_exact, hyy_exact
        real(wp) :: gx, gy, hxx, hxy, hyy
        real(wp), allocatable :: f(:)

        integer :: n

        n = size(x)

        allocate(f(size(x)))

        select case (name)
        case ("1")
            f = 1.0_wp
        case ("x")
            f = x
        case ("y")
            f = y
        case ("x^2")
            f = x**2
        case ("y^2")
            f = y**2
        case ("x*y")
            f = x*y
        case ("general quad")
            f = 1 + 2*x - y + 3*x**2 + 4*x*y + 5*y**2
        end select

        gx  = sum(coeffs(1:n,1) * f)
        gy  = sum(coeffs(1:n,2) * f)
        hxx = sum(coeffs(1:n,3) * f)
        hxy = sum(coeffs(1:n,4) * f)
        hyy = sum(coeffs(1:n,5) * f)

        print '(/,A,1X,A)', "Testing", trim(name)
        print '(A,2F12.6)', "Grad (approx) ", gx, gy
        print '(A,2F12.6)', "Grad (exact)  ", gx_exact, gy_exact
        print '(A,3F12.6)', "Hess (approx) ", hxx, hxy, hyy
        print '(A,3F12.6)', "Hess (exact)  ", hxx_exact, hxy_exact, hyy_exact

    end subroutine test_quadratic


    subroutine test_smooth(x, y, coeffs, xc, yc)
        real(wp), intent(in) :: x(:), y(:)        ! coordinates (x, y)
        real(wp), intent(in) :: coeffs(:,:)       ! RBF-FD weights
        real(wp), intent(in) :: xc, yc            ! stencil center
        real(wp) :: gx, gy, hxx, hxy, hyy
        real(wp) :: gx_exact, gy_exact, hxx_exact, hxy_exact, hyy_exact
        real(wp), allocatable :: f(:)
        integer :: n

        real(wp), parameter :: pi = 4.0_wp*atan(1.0_wp)

        n = size(x)
        allocate(f(n))

        ! define f(x,y) = sin(pi x) * cos(pi y)
        f = sin(pi*x) * cos(pi*y)

        ! compute derivatives using RBF-FD weights
        gx  = sum(coeffs(1:n,1) * f)
        gy  = sum(coeffs(1:n,2) * f)
        hxx = sum(coeffs(1:n,3) * f)
        hxy = sum(coeffs(1:n,4) * f)
        hyy = sum(coeffs(1:n,5) * f)

        ! compute exact derivatives at (xc, yc)
        gx_exact  = pi * cos(pi*xc) * cos(pi*yc)
        gy_exact  = -pi * sin(pi*xc) * sin(pi*yc)
        hxx_exact = -pi**2 * sin(pi*xc) * cos(pi*yc)
        hxy_exact = -pi**2 * cos(pi*xc) * sin(pi*yc)
        hyy_exact = -pi**2 * sin(pi*xc) * cos(pi*yc)

        print '(/,A)', "Testing smooth function f(x,y) = sin(pi x)*cos(pi y)"
        print '(A,2F12.6)', "Grad (approx) ", gx, gy
        print '(A,2F12.6)', "Grad (exact)  ", gx_exact, gy_exact
        print '(A,3F12.6)', "Hess (approx) ", hxx, hxy, hyy
        print '(A,3F12.6)', "Hess (exact)  ", hxx_exact, hxy_exact, hyy_exact

    end subroutine

end program test_phs_poly
