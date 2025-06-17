# package only provides headers
%global debug_package %{nil}
%define oname earcut.hpp

%bcond_without tests

Name:		earcut-hpp
Version:	2.2.4
Release:	1
Summary:	A C++ port of earcut.js, a fast, header-only polygon triangulation library
URL:		https://github.com/mapbox/earcut.hpp
License:	ISC
Group:		Development/Libraries/C and C++
Source0:	https://github.com/mapbox/earcut.hpp/archive/v%{version}/%{oname}-%{version}.tar.gz
# Patch Fix unused but set variable
Patch0:		https://github.com/mapbox/earcut.hpp/commit/a30c14b5676adabe4714ff4173dae8a5d568ab59.patch
# Patch Include <cstdint> for uint32_t/int32_t
Patch1:		https://github.com/mapbox/earcut.hpp/commit/7fa7aa30183849e988ae79ab2eef19f9ae97acf4.patch

BuildRequires:	cmake
BuildRequires:	ninja
# For BUILD_VIZ if enabled
BuildRequires:	pkgconfig(glfw3)
# For tests (and benchmarks, if enabled):
BuildRequires:	pkgconfig(opengl)
%global _description %{expand:
A C++ port of earcut.js, a fast, header-only polygon triangulation library.

The library implements a modified ear slicing algorithm, optimized by z-order
curve hashing and extended to handle holes, twisted polygons, degeneracies
and self-intersections in a way that doesn't guarantee correctness of
triangulation, but attempts to always produce acceptable results for practical
data like geographical shapes.

It's based on ideas from FIST: Fast Industrial-Strength Triangulation of
Polygons by Martin Held and Triangulation by Ear Clipping by David Eberly.
}

%description %{_description}

%package devel
Summary:	Development headers for %{name}
Group:		Development/C
BuildArch:	noarch

Provides:	%{name}-static = %{version}-%{release}

%description devel
Development files (Headers etc.) for %{name}.

%{_description}

%prep
%autosetup -n %{oname}-%{version} -p1

# Increase precision of test output so we can understand any failures:
sed -r -i 's/(setprecision\()6(\))/\116\2/' test/test.cpp
# Disabling floating-point contraction fixes certain failures on aarch64,
# ppc64le, and s390x. See:
#
#   Test “self_touching” fails on aarch64, ppc64le, s390x
#   https://github.com/mapbox/earcut.hpp/issues/97
# particularly
#   https://github.com/mapbox/earcut.hpp/issues/97#issuecomment-1032813710
# and also
#   New test “issue142” in 2.2.4 fails on aarch64, ppc64le, s390x
#   https://github.com/mapbox/earcut.hpp/issues/103
#
# Since this library is header-only, dependent packages should be advised to
# add this flag too if they want the behavior of the library to exactly match
# upstream’s expectations.
export CXXFLAGS="${CXXFLAGS-} -ffp-contract=off"
# We do want to build the tests, but we have no use for the benchmarks or the
# visualizer program.
%cmake \
    -DEARCUT_BUILD_TESTS:BOOL=ON \
    -DEARCUT_BUILD_BENCH:BOOL=OFF \
    -DEARCUT_BUILD_VIZ:BOOL=OFF \
    -DEARCUT_WARNING_IS_ERROR:BOOL=OFF \
    -G Ninja

%build
%ninja_build -C build

%install
# upstream provide no install target, install header file manually
install -D -t '%{buildroot}%{_includedir}/mapbox' -p -m 0644 \
    'include/mapbox/earcut.hpp'

%if %{with tests}
# upstream has not configured to run tests with ctests,
# can be run manually with built tests executable
%check
%{_vpath_builddir}/tests
%endif

%files devel
# All -devel packages for C and C++ libraries from Mapbox should co-own this
# directory.
%dir %{_includedir}/mapbox
%{_includedir}/mapbox/earcut.hpp
%doc README.md
%license LICENSE

