subroutine c_phs3_p2(n,x,y,coeffs,ldc,wrk,iwrk,ierr) bind(c)
    use phs_poly_approx, only: phs3_poly2
    use, intrinsic :: iso_c_binding, only: c_int, c_double
    integer(c_int), intent(in) :: n, ldc
    real(c_double), intent(in) :: x(n), y(n)
    real(c_double), intent(out) :: coeffs(ldc,5)
    real(c_double), intent(inout) :: wrk(ldc,n + 6)
    integer(c_int), intent(inout) :: iwrk(n+6)
    integer(c_int), intent(out) :: ierr
    call phs3_poly2(n,x,y,coeffs,ldc,wrk,iwrk,ierr)
end subroutine

subroutine c_phs3_p3(n,x,y,coeffs,ldc,wrk,iwrk,ierr) bind(c)
    use phs_poly_approx, only: phs3_poly3
    use, intrinsic :: iso_c_binding, only: c_int, c_double
    integer(c_int), intent(in) :: n, ldc
    real(c_double), intent(in) :: x(n), y(n)
    real(c_double), intent(out) :: coeffs(ldc,5)
    real(c_double), intent(inout) :: wrk(ldc,n + 10)
    integer(c_int), intent(inout) :: iwrk(n + 10)
    integer(c_int), intent(out) :: ierr
    call phs3_poly3(n,x,y,coeffs,ldc,wrk,iwrk,ierr)
end subroutine
