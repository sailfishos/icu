Name:      icu
Version:   4.6
Release:   8
Summary:   International Components for Unicode
Group:     Development/Tools
License:   MIT
URL:       http://www.icu-project.org/
Source0:   %{name}-%{version}.tar.gz
Source1:   icu-config
BuildRequires: doxygen, autoconf
Requires: lib%{name} = %{version}-%{release}

%description
Tools and utilities for developing with icu.

%package -n lib%{name}
Summary: International Components for Unicode - libraries
Group:   System/Libraries

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
Requires: lib%{name} = %{version}-%{release}
Requires: pkgconfig
Requires: %{name} = %{version}-%{release}

%description -n lib%{name}-devel
Includes and definitions for developing with icu.

%package -n lib%{name}-doc
Summary: Documentation for International Components for Unicode
Group:   Documentation
BuildArch: noarch

%description -n lib%{name}-doc
%{summary}.

%prep
%setup -q -n %{name}-%{version}/%{name}

%build
cd source
autoconf
%configure --with-data-packaging=library --disable-samples --disable-renaming
#rhbz#225896
sed -i -- "s/-nodefaultlibs -nostdlib//" config/mh-linux
make # %{?_smp_mflags} # -j(X>1) may "break" man pages as of 3.2, b.f.u #2357
make doc

%install
rm -rf $RPM_BUILD_ROOT source/__docs
make -C source install DESTDIR=$RPM_BUILD_ROOT
make -C source install-doc docdir=__docs
chmod +x $RPM_BUILD_ROOT%{_libdir}/*.so.*
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}/%{name}-config
chmod 0755 $RPM_BUILD_ROOT%{_bindir}/%{name}-config

find source/__docs/%{name}/html/ -type f -exec chmod a-x {} \;

%check
%if ! 0%{?qemu_user_space_build}
# qemu-arm locks up currently on  ---OK:   TestMutex 
# we're working on resolving this - meantime: disable make check on ARM
make -C source check
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n lib%{name} -p /sbin/ldconfig

%postun -n lib%{name} -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc license.html readme.html
%{_bindir}/derb
%{_bindir}/genbrk
%{_bindir}/gencfu
%{_bindir}/gencnval
%{_bindir}/genctd
%{_bindir}/genrb
%{_bindir}/makeconv
%{_bindir}/pkgdata
%{_bindir}/uconv
%{_bindir}/icuinfo
%{_sbindir}/*
%{_mandir}/man1/derb.1*
%{_mandir}/man1/gencnval.1*
%{_mandir}/man1/genrb.1*
%{_mandir}/man1/genbrk.1*
%{_mandir}/man1/genctd.1*
%{_mandir}/man1/makeconv.1*
%{_mandir}/man1/pkgdata.1*
%{_mandir}/man1/uconv.1*
%{_mandir}/man8/*.8*

%files -n lib%{name}
%defattr(-,root,root,-)
%{_libdir}/*.so.*

%files -n lib%{name}-devel
%defattr(-,root,root,-)
%{_bindir}/%{name}-config
%{_mandir}/man1/%{name}-config.1*
%{_includedir}/layout
%{_includedir}/unicode
%{_libdir}/*.so
%{_libdir}/pkgconfig/icu-*.pc
%{_libdir}/%{name}
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/%{version}
%{_datadir}/%{name}/%{version}/install-sh
%{_datadir}/%{name}/%{version}/mkinstalldirs
%{_datadir}/%{name}/%{version}/config
%doc %{_datadir}/%{name}/%{version}/license.html

%files -n lib%{name}-doc
%defattr(-,root,root,-)
%doc source/__docs/%{name}/html/*

