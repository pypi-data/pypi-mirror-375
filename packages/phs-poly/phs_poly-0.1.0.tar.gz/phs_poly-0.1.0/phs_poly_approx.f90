!  phs_poly_approx.f90
!
!  Copyright (c) 2025 Ivan Pribec <ivan.pribec@gmail.com>
!
!  This file is distributed under the MIT license.
!  See the full license text at: https://opensource.org/licenses/MIT
!
!  SPDX-License-Identifier: MIT

!***********************************************************************
!
!  MODULE: phs_poly_approx
!
!  Purpose
!  =======
!  Provides routines for generating radial-basis-function-generated finite-
!  difference (RBF-FD) weights using polyharmonic splines (PHS) with polynomial
!  augmentation. The weights approximate first- and second-order partial
!  derivatives (gradient and Hessian) at a stencil center.
!
!  Description
!  ===========
!  Polynomial augmentation guarantees exact reproduction of polynomials up to
!  the chosen degree and avoids stagnation errors, while the RBF part provides
!  stability and robustness without requiring a shape parameter.
!
!  Stencil size
!  ============
!  The number of monomial terms required for polynomial reproduction is
!
!      M = binomial(p + d, p),
!
!  where p is the polynomial degree and d = 2 in two dimensions.
!  For example:
!      p = 1  ->  M = 3
!      p = 2  ->  M = 6
!      p = 3  ->  M = 10
!
!  To ensure stability and accuracy, several authors recommend that the stencil
!  should contain at least 2*M nodes, i.e. twice the number of polynomial terms
!  in the augmentation space.
!
!  References
!  ==========
!  Bayona, S., Flyer, N., Fornberg, B., Barnett, G. (2019).
!  "An insight into RBF-FD approximations augmented with polynomials",
!  Computers & Mathematics with Applications, 77(9), 2337–2353.
!  https://doi.org/10.1016/j.camwa.2019.01.034
!
!  Features
!  ========
!  - Simple, robust, fully local weight computation on scattered stencils
!  - No shape parameter tuning required
!  - Polynomial augmentation ensures exact reproduction of quadratics/cubics
!  - Supports gradient and Hessian approximation
!
module phs_poly_approx

use, intrinsic :: iso_fortran_env, only: error_unit

implicit none
private

public :: phs3_poly2, phs3_poly3

integer, parameter :: dp = kind(1.0d0)

contains

!***********************************************************************
!  PHS3_POLY2
!
!  Purpose
!  =======
!
!  PHS3_POLY2 computes finite-difference weights for approximating
!  first- and second-order partial derivatives (gradient and Hessian)
!  of a function f(x,y) at the origin, using a polyharmonic spline
!  (PHS) radial basis function of order q=3 augmented with quadratic
!  polynomials.
!
!  The method solves the saddle-point system
!
!     [ A   P ] [ w ] = [ d ]
!     [ P^T 0 ] [ λ ]   [ 0 ]
!
!  where A_ij = ||x_i - x_j||^3, P contains quadratic polynomial
!  terms, and d encodes the desired differential operator.
!
!  Arguments
!  =========
!
!  N       (input) INTEGER
!          Number of stencil nodes (must be >= 6).
!
!  X, Y    (input) REAL(KIND=dp) arrays, dimension (N)
!          Coordinates of the stencil nodes relative to the
!          evaluation point (usually shifted so that (0,0) is
!          the target).
!
!  COEFFS  (output) REAL(KIND=dp) array, dimension (LDC,5)
!          Columns of weights for the following operators:
!            1: ∂/∂x
!            2: ∂/∂y
!            3: ∂²/∂x²
!            4: ∂²/∂x∂y
!            5: ∂²/∂y²
!
!  LDC     (input) INTEGER
!          Leading dimension of COEFFS and WRK. Must be at least N+6.
!
!  WRK     (workspace) REAL(KIND=dp) array, dimension (LDC,N+6)
!          Workspace to hold the system matrix during factorization.
!
!  IWRK    (workspace) INTEGER array, dimension (N+6)
!          Pivot indices for DGESV.
!
!  IERR    (output) INTEGER
!          = 0: successful exit
!          < 0: if IERR = -k, the k-th input argument had an illegal value
!          > 0: if IERR =  k, the system could not be solved (singular).
!
!  External routines
!  =================
!
!  DGESV   (from LAPACK) is used to solve the linear system.
!
!  Notes
!  =====
!
!  - Quadratic polynomials are reproduced exactly.
!  - Stencil should contain at least 6 points for stability.
!
!***********************************************************************
subroutine phs3_poly2(n,x,y,coeffs,ldc,wrk,iwrk,ierr)
    integer, intent(in) :: n, ldc
    real(dp), intent(in) :: x(n), y(n)
    real(dp), intent(out) :: coeffs(ldc,5)
    real(dp), intent(inout) :: wrk(ldc,n + 6)
    integer, intent(inout) :: iwrk(n+6)
    integer, intent(out) :: ierr

    external :: dgesv
    integer :: np, k

    np = n + 6
!
! Test the input parameters
!
    ierr = 0
    if (n < 6) then
        ierr = -1
    else if (ldc < np) then
        ierr = -5
    end if
    if (ierr /= 0) then
        write(error_unit,'(A,I0)') "PHS3_POLY2: returned with IERR = ", -ierr
        return
    end if

!
! Fill matrix M = [ A, P; P^T 0]
!

    ! [ A; P^T ] - block
    do k = 1, n
        call phs3_poly_basis(n,x,y,x(k),y(k),wrk(1:np,k))
    end do

    ! P-block
    wrk(1:n,n+1:np) = transpose(wrk(n+1:np,1:n))

    ! Zero-block
    wrk(n+1:np,n+1:np) = 0.0_dp

!
! Calculate derivative operators
!
    call phs3_poly_der(n,x,y,coeffs,ldc)

!
! Compute the LU factorization and solve the linear system for the weights
!
    call dgesv(np,5,wrk,ldc,iwrk,coeffs,ldc,ierr)
    if (ierr < 0) error stop "phs3_poly2: error in DGESV call"

contains

    subroutine phs3_poly_basis(n,x,y,xc,yc,b)
        integer, intent(in) :: n
        real(dp), intent(in) :: x(n), y(n)
        real(dp), intent(in) :: xc, yc
        real(dp), intent(out) :: b(n+6)

        integer, parameter :: q = 3

        ! RBF part
        associate(r => hypot(xc - x, yc - y))
            b(1:n) = r**q
        end associate

        ! Polynomial part
        b(n+1) = 1.0_dp
        b(n+2) = xc
        b(n+3) = yc
        b(n+4) = xc*xc
        b(n+5) = xc*yc
        b(n+6) = yc*yc

    end subroutine

    subroutine phs3_poly_der(n,x,y,coeffs,ldc)
        integer, intent(in) :: n, ldc
        real(dp), intent(in) :: x(n), y(n)
        real(dp), intent(inout) :: coeffs(ldc,5)

        ! RBF derivatives
        associate(r => hypot(x,y))

            coeffs(1:n,1) = -3*r*x
            coeffs(1:n,2) = -3*r*y

            coeffs(1:n,3) = (6*x**2 + 3*y**2)
            coeffs(1:n,4) = 3*x*y
            coeffs(1:n,5) = (3*x**2 + 6*y**2)

            where (r > 0)
                coeffs(1:n,3) = coeffs(1:n,3) / r
                coeffs(1:n,4) = coeffs(1:n,4) / r
                coeffs(1:n,5) = coeffs(1:n,5) / r
            end where

        end associate

        ! Polynomial part
        coeffs(n+1:np,1:5) = 0.0_dp

        coeffs(n+2,1) = 1.0_dp
        coeffs(n+3,2) = 1.0_dp

        coeffs(n+4,3) = 2.0_dp
        coeffs(n+5,4) = 1.0_dp
        coeffs(n+6,5) = 2.0_dp

    end subroutine

end subroutine


!***********************************************************************
!  PHS3_POLY3
!
!  Purpose
!  =======
!
!  PHS3_POLY3 is identical to PHS3_POLY2 except that the RBF system
!  is augmented with cubic polynomials, improving accuracy for smooth
!  functions. The null space dimension increases from 6 to 10.
!
!  Arguments
!  =========
!
!  N       (input) INTEGER
!          Number of stencil nodes (must be >= 10).
!
!  X, Y    (input) REAL(KIND=dp) arrays, dimension (N)
!          Coordinates of the stencil nodes relative to the
!          evaluation point.
!
!  COEFFS  (output) REAL(KIND=dp) array, dimension (LDC,5)
!          Differential operator weights, as in PHS3_POLY2.
!
!  LDC     (input) INTEGER
!          Leading dimension of COEFFS and WRK. Must be at least N+10.
!
!  WRK     (workspace) REAL(KIND=dp) array, dimension (LDC,N+10)
!          Workspace to hold the system matrix during factorization.
!
!  IWRK    (workspace) INTEGER array, dimension (N+10)
!          Pivot indices for DGESV.
!
!  IERR    (output) INTEGER
!          = 0: successful exit
!          < 0: if IERR = -k, the k-th input argument had an illegal value
!          > 0: if IERR =  k, the system could not be solved (singular).
!
!  Notes
!  =====
!
!  - All cubic polynomials are reproduced exactly.
!  - Stencil should contain at least 10 points.
!
!***********************************************************************
subroutine phs3_poly3(n,x,y,coeffs,ldc,wrk,iwrk,ierr)
    integer, intent(in) :: n, ldc
    real(dp), intent(in) :: x(n), y(n)
    real(dp), intent(out) :: coeffs(ldc,5)
    real(dp), intent(inout) :: wrk(ldc,n + 10)
    integer, intent(inout) :: iwrk(n + 10)
    integer, intent(out) :: ierr

    external :: dgesv
    integer :: np, k

    np = n + 10
!
! Test the input parameters
!
    ierr = 0
    if (n < 10) then
        ierr = -1
    else if (ldc < np) then
        ierr = -5
    end if
    if (ierr /= 0) then
        write(error_unit,'(A,I0)') "PHS3_POLY2: returned with IERR = ", -ierr
        return
    end if

!
! Fill matrix M = [ A, P; P^T 0]
!

    ! [ A; P^T ] - block
    do k = 1, n
        call phs3_poly_basis(n,x,y,x(k),y(k),wrk(1:np,k))
    end do

    ! P-block
    wrk(1:n,n+1:np) = transpose(wrk(n+1:np,1:n))

    ! Zero-block
    wrk(n+1:np,n+1:np) = 0.0_dp

!
! Calculate derivative operators
!
    call phs3_poly_der(n,x,y,coeffs,ldc)

!
! Compute the LU factorization and solve the linear system for the weights
!
    call dgesv(np,5,wrk,ldc,iwrk,coeffs,ldc,ierr)
    if (ierr < 0) error stop "phs3_poly2: error in DGESV call"

contains

    subroutine phs3_poly_basis(n,x,y,xc,yc,b)
        integer, intent(in) :: n
        real(dp), intent(in) :: x(n), y(n)
        real(dp), intent(in) :: xc, yc
        real(dp), intent(out) :: b(n + 10)

        integer, parameter :: q = 3

        ! RBF part
        associate(r => hypot(xc - x, yc - y))
            b(1:n) = r**q
        end associate

        ! Polynomial part
        b(n+1) = 1.0_dp
        b(n+2) = xc
        b(n+3) = yc
        b(n+4) = xc*xc
        b(n+5) = xc*yc
        b(n+6) = yc*yc
        b(n+7)  = xc*xc*xc
        b(n+8)  = xc*xc*yc
        b(n+9)  = xc*yc*yc
        b(n+10) = yc*yc*yc

    end subroutine

    subroutine phs3_poly_der(n,x,y,coeffs,ldc)
        integer, intent(in) :: n, ldc
        real(dp), intent(in) :: x(n), y(n)
        real(dp), intent(inout) :: coeffs(ldc,5)

        integer :: np

        np = n + 10

        ! RBF derivatives
        associate(r => hypot(x,y))

            coeffs(1:n,1) = -3*r*x
            coeffs(1:n,2) = -3*r*y

            coeffs(1:n,3) = (6*x**2 + 3*y**2)
            coeffs(1:n,4) = 3*x*y
            coeffs(1:n,5) = (3*x**2 + 6*y**2)

            where (r > 0)
                coeffs(1:n,3) = coeffs(1:n,3) / r
                coeffs(1:n,4) = coeffs(1:n,4) / r
                coeffs(1:n,5) = coeffs(1:n,5) / r
            end where

        end associate

        ! Polynomial part
        coeffs(n+1:np,:) = 0.0_dp

        coeffs(n+2,1) = 1.0_dp
        coeffs(n+3,2) = 1.0_dp

        coeffs(n+4,3) = 2.0_dp
        coeffs(n+5,4) = 1.0_dp
        coeffs(n+6,5) = 2.0_dp

    end subroutine

end subroutine

end module phs_poly_approx
