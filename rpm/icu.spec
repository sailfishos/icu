%define upstream_version 70.1
Name:      icu
Version:   %{upstream_version}
Release:   1
Summary:   International Components for Unicode
License:   MIT and UCD and Public Domain
URL:       http://site.icu-project.org/
Source0:   %{name}-%{version}.tar.gz
BuildRequires: autoconf, doxygen, python3-base
Requires: lib%{name}%{?_isa} = %{version}-%{release}

Patch1: 0001-Disable-failing-tests.patch

%description
Tools and utilities for developing with icu.

%package -n lib%{name}
Summary: International Components for Unicode - libraries

%description -n lib%{name}
The International Components for Unicode (ICU) libraries provide
robust and full-featured Unicode services on a wide variety of
platforms. ICU supports the most current version of the Unicode
standard, and they provide support for supplementary Unicode
characters (needed for GB 18030 repertoire support).
As computing environments become more heterogeneous, software
portability becomes more important. ICU lets you produce the same
results across all the various platforms you support, without
sacrificing performance. It offers great flexibility to extend and
customize the supplied services.

%package  -n lib%{name}-devel
Summary:  Development files for International Components for Unicode
Requires: lib%{name}%{?_isa} = %{version}-%{release}
Requires: %{name} = %{version}-%{release}
Requires: pkgconfig

%description -n lib%{name}-devel
Includes and definitions for developing with icu.

%package -n lib%{name}-doc
Summary: Documentation for International Components for Unicode
BuildArch: noarch

%description -n lib%{name}-doc
Documentation and man pages for International Components for Unicode.

%{!?endian: %global endian %(%{__python} -c "import sys;print (0 if sys.byteorder=='big' else 1)")}
# " this line just fixes syntax highlighting for vim that is confused by the above and continues literal

%prep
%autosetup -p1 -n %{name}-%{version}/upstream

%build
cd icu4c/source
autoconf
CFLAGS='%optflags -fno-strict-aliasing'
CXXFLAGS='%optflags -fno-strict-aliasing'
# Endian: BE=0 LE=1
%if ! 0%{?endian}
CPPFLAGS='-DU_IS_BIG_ENDIAN=1'
%endif
#rhbz856594 do not use --disable-renaming or cope with the mess
%configure --with-data-packaging=library --disable-samples --disable-renaming

#rhbz#225896
sed -i 's|-nodefaultlibs -nostdlib||' config/mh-linux
#rhbz#813484
#sed -i 's| \$(docfilesdir)/installdox||' Makefile
# There is no source/doc/html/search/ directory
#sed -i '/^\s\+\$(INSTALL_DATA) \$(docsrchfiles) \$(DESTDIR)\$(docdir)\/\$(docsubsrchdir)\s*$/d' Makefile
# rhbz#856594 The configure --disable-renaming and possibly other options
# result in icu/source/uconfig.h.prepend being created, include that content in
# icu/source/common/unicode/uconfig.h to propagate to consumer packages.
test -f uconfig.h.prepend && sed -e '/^#define __UCONFIG_H__/ r uconfig.h.prepend' -i common/unicode/uconfig.h

%make_build
%make_build doc

%install
rm -rf $RPM_BUILD_ROOT icu4c/source/__docs
%make_build -C icu4c/source install DESTDIR=$RPM_BUILD_ROOT
%make_build -C icu4c/source install-doc \
     docdir=$RPM_BUILD_ROOT/%{_docdir}/%{name}-%{version}
chmod +x $RPM_BUILD_ROOT%{_libdir}/*.so.*

%check
# test to ensure that -j(X>1) didn't "break" man pages. b.f.u #2357
if grep -q @VERSION@ icu4c/source/tools/*/*.8 icu4c/source/tools/*/*.1 icu4c/source/config/*.1; then
    exit 1
fi
%make_build -C icu4c/source check

%post -n lib%{name} -p /sbin/ldconfig

%postun -n lib%{name} -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%{_bindir}/derb
%{_bindir}/genbrk
%{_bindir}/gencfu
%{_bindir}/gencnval
%{_bindir}/gendict
%{_bindir}/genrb
%{_bindir}/makeconv
%{_bindir}/pkgdata
%{_bindir}/uconv
%{_sbindir}/*

%files -n lib%{name}
%defattr(-,root,root,-)
%license %{_datadir}/icu/%{upstream_version}/LICENSE
%{_libdir}/*.so.*

%files -n lib%{name}-devel
%defattr(-,root,root,-)
%{_bindir}/icu-config*
%{_bindir}/icuinfo
%{_bindir}/icuexportdata
%{_includedir}/unicode
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc
%{_libdir}/icu
%dir %{_datadir}/icu
%dir %{_datadir}/icu/%{upstream_version}
%{_datadir}/icu/%{upstream_version}/install-sh
%{_datadir}/icu/%{upstream_version}/mkinstalldirs
%{_datadir}/icu/%{upstream_version}/config

%files -n lib%{name}-doc
%defattr(-,root,root,-)
%{_mandir}/man*/*.*
%{_docdir}/%{name}-%{version}
