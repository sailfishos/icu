%define upstream_version 52.1
Name:      icu52
Version:   %{upstream_version}
Release:   10%{?dist}
Summary:   International Components for Unicode
Group:     Development/Tools
License:   MIT and UCD and Public Domain
URL:       http://www.icu-project.org/
Source0:   %{name}-%{version}.tar.gz
BuildRequires: autoconf, python, doxygen
Requires: lib%{name}%{?_isa} = %{version}-%{release}

%description
Tools and utilities for developing with icu.

%package -n lib%{name}
Summary: International Components for Unicode - libraries
Group:   System Environment/Libraries

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
Group:    Development/Libraries
Requires: lib%{name}%{?_isa} = %{version}-%{release}
Requires: %{name} = %{version}-%{release}
Requires: pkgconfig

%description -n lib%{name}-devel
Includes and definitions for developing with icu.

%package -n lib%{name}-doc
Summary: Documentation for International Components for Unicode
Group:   Documentation
BuildArch: noarch

%description -n lib%{name}-doc
Documentation and man pages for International Components for Unicode.

%{!?endian: %global endian %(%{__python} -c "import sys;print (0 if sys.byteorder=='big' else 1)")}
# " this line just fixes syntax highlighting for vim that is confused by the above and continues literal

%prep
%setup -q -n %{name}-%{version}/icu

%build
cd source
autoconf
CFLAGS='%optflags -fno-strict-aliasing'
CXXFLAGS='%optflags -fno-strict-aliasing'
# Endian: BE=0 LE=1
%if ! 0%{?endian}
CPPFLAGS='-DU_IS_BIG_ENDIAN=1'
%endif
#rhbz856594 do not use --disable-renaming or cope with the mess
#test
%configure --with-data-packaging=library --disable-samples --disable-renaming
#rhbz#225896
sed -i 's|-nodefaultlibs -nostdlib||' config/mh-linux
#rhbz#681941
#sed -i 's|^LIBS =.*|LIBS = -L../lib -licuuc -lpthread -lm|' i18n/Makefile
#sed -i 's|^LIBS =.*|LIBS = -nostdlib -L../lib -licuuc -licui18n -lc -lgcc|' io/Makefile
#sed -i 's|^LIBS =.*|LIBS = -nostdlib -L../lib -licuuc -lc|' layout/Makefile
#sed -i 's|^LIBS =.*|LIBS = -nostdlib -L../lib -licuuc -licule -lc|' layoutex/Makefile
#sed -i 's|^LIBS =.*|LIBS = -nostdlib -L../../lib -licutu -licuuc -lc|' tools/ctestfw/Makefile
#sed -i 's|^LIBS =.*|LIBS = -nostdlib -L../../lib -licui18n -licuuc -lpthread -lc|' tools/toolutil/Makefile
#rhbz#813484
#sed -i 's| \$(docfilesdir)/installdox||' Makefile
# There is no source/doc/html/search/ directory
#sed -i '/^\s\+\$(INSTALL_DATA) \$(docsrchfiles) \$(DESTDIR)\$(docdir)\/\$(docsubsrchdir)\s*$/d' Makefile
# rhbz#856594 The configure --disable-renaming and possibly other options
# result in icu/source/uconfig.h.prepend being created, include that content in
# icu/source/common/unicode/uconfig.h to propagate to consumer packages.
test -f uconfig.h.prepend && sed -e '/^#define __UCONFIG_H__/ r uconfig.h.prepend' -i common/unicode/uconfig.h

make %{?_smp_mflags}
make %{?_smp_mflags} doc

%install
rm -rf $RPM_BUILD_ROOT source/__docs
make %{?_smp_mflags} -C source install DESTDIR=$RPM_BUILD_ROOT
make %{?_smp_mflags} -C source install-doc \
     docdir=$RPM_BUILD_ROOT/%{_docdir}/%{name}-%{version}
chmod +x $RPM_BUILD_ROOT%{_libdir}/*.so.*

%check
# test to ensure that -j(X>1) didn't "break" man pages. b.f.u #2357
if grep -q @VERSION@ source/tools/*/*.8 source/tools/*/*.1 source/config/*.1; then
    exit 1
fi
make %{?_smp_mflags} -C source check

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
%license license.html
%{_libdir}/*.so.*

%files -n lib%{name}-devel
%defattr(-,root,root,-)
%{_bindir}/icu-config*
%{_bindir}/icuinfo
%{_includedir}/layout
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
