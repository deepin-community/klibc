Summary: A minimal libc subset for use with initramfs.
Name: klibc
Version: 2.0.13
Release: 1
License: BSD/GPL
Group: Development/Libraries
URL: https://www.zytor.com/mailman/listinfo/klibc
Source: https://www.kernel.org/pub/linux/libs/klibc/2.0/klibc-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: kernel >= 2.6.0, kernel-devel
Packager: H. Peter Anvin <hpa@zytor.com>
Prefix: /usr
Vendor: Starving Linux Artists

%define klibcdir  %{_prefix}/lib/klibc
%define libdocdir %{_docdir}/%{name}-%{version}-%{release}
%define bindocdir %{_docdir}/%{name}-utils-%{version}-%{release}

%description
%{name} is intended to be a minimalistic libc subset for use with
initramfs.  It is deliberately written for small size, minimal
entanglement, and portability, not speed.

%package devel
Summary: Libraries and tools needed to compile applications against klibc.
Group: Development/Libraries
Requires: klibc = %{version}-%{release}

%description devel
This package contains the link libraries, header files, and gcc
wrapper scripts needed to compile applications against klibc.

%package utils
Summary: Small utilities built with klibc.
Group: Utilities/System
Requires: klibc = %{version}-%{release}

%description utils
This package contains a collection of programs that are linked against
klibc.  These duplicate some of the functionality of a regular Linux
toolset, but are typically much smaller than their full-function
counterparts.  They are intended for inclusion in initramfs images and
embedded systems.

%prep
%setup -q
cp -dRs /lib/modules/`uname -r`/build/ ./linux
# Shouldn't need this when getting the build tree from /lib/modules
# make -C linux defconfig ARCH=%{_target_cpu}
# make -C linux prepare ARCH=%{_target_cpu}
# Deal with braindamage in RedHat's kernel-source RPM
rm -f linux/include/linux/config.h
cat <<EOF > linux/include/linux/config.h
#ifndef _LINUX_CONFIG_H
#define _LINUX_CONFIG_H

#include <linux/autoconf.h>

#endif
EOF
mkdir -p %{buildroot}

%build
make %{_smp_mflags} \
	KLIBCARCH=%{_target_cpu} prefix=%{_prefix} bindir=%{_bindir} \
	INSTALLDIR=%{klibcdir} mandir=%{_mandir} INSTALLROOT=%{buildroot}

%install
rm -rf %{buildroot}
make  KLIBCARCH=%{_target_cpu} prefix=%{_prefix} bindir=%{_bindir} \
	INSTALLDIR=%{klibcdir} mandir=%{_mandir} INSTALLROOT=%{buildroot} \
	install

# Make the .so file in /lib a hardlink (they will be expanded as two
# files automatically if it crosses filesystems when extracted.)
ln -f %{buildroot}%{klibcdir}/lib/klibc-*.so %{buildroot}/lib

# Install the docs
mkdir -p %{buildroot}%{bindocdir} %{buildroot}%{libdocdir}
install -m 444 README %{buildroot}%{libdocdir}
install -m 444 usr/klibc/README.klibc %{buildroot}%{libdocdir}
install -m 444 usr/klibc/arch/README.klibc.arch %{buildroot}%{libdocdir}

install -m 444 usr/gzip/COPYING %{buildroot}%{bindocdir}/COPYING.gzip
install -m 444 usr/gzip/README %{buildroot}%{bindocdir}/README.gzip
install -m 444 usr/kinit/ipconfig/README.ipconfig %{buildroot}%{bindocdir}
install -m 444 usr/kinit/README %{buildroot}%{bindocdir}/README.kinit

%clean
rm -rf $RPM_BUILD_ROOT

#
# Note: libc.so and shared-stub.o are technically -devel files, but
# put them in this package until we can make really, really sure
# the dependency system can avoid confusion.  (In fact, it would be
# good to eventually get them out of here, so that multiple runtimes
# can be installed should it be necessary.)
#
%files
%defattr(-,root,root,-)
/lib/klibc-*.so
%{klibcdir}/lib/*.so
%{klibcdir}/lib/shared-stub.o

%files devel
%defattr(-,root,root,-)
%{klibcdir}/include
%{klibcdir}/lib/*.a
%{klibcdir}/lib/crt0.o
%{_bindir}/klcc
%doc %{_mandir}/man1/*
%doc %{libdocdir}/*

%files utils
%defattr(-,root,root,-)
%{klibcdir}/bin
%doc %{bindocdir}/*

%changelog
* Tue Mar 1 2005 H. Peter Anvin <hpa@zytor.com>
- New "make install" scheme, klcc

* Tue Jul 6 2004 H. Peter Anvin <hpa@zytor.com>
- Update to use kernel-source RPM for the kernel symlink.

* Sat Nov 29 2003 Bryan O'Sullivan <bos@serpentine.com> -
- Initial build.
