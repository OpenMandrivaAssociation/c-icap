%define major 0
%define libname %mklibname c-icap %{major}
%define develname %mklibname c-icap -d

%define epoch 2

Summary:	An ICAP server coded in C
Name:		c-icap
Version:	180407
Release:	%mkrel 1
License:	GPL
Group:		System/Servers
URL:		http://sourceforge.net/projects/c-icap/
Source0:	http://prdownloads.sourceforge.net/c-icap/c_icap-%{version}.tar.gz
Source1:	icapd.init
Source2:	icapd.sysconfig
Source3:	icapd.logrotate
Patch0:		c_icap-mdv_conf.diff
Patch1:		c_icap-makefile.patch
Patch2:		c_icap-030606-perllib_fix.patch
Patch3:		c_icap-clamav-0.93_build_fix.diff
BuildRequires:	clamav-devel
BuildRequires:	chrpath
BuildRequires:	dos2unix
BuildRequires:	automake1.7
BuildRequires:	autoconf2.5
BuildRequires:	perl-devel
BuildRequires:	libcurl-devel
BuildRequires:	libbzip2-devel
BuildRequires:	libidn-devel
BuildRequires:	libgmp-devel
BuildRequires:	openssl-devel
Epoch:		%{epoch}
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
An ICAP server coded in C

%package -n	%{libname}
Summary:	Shared libraries for %{name}
Group:		System/Libraries

%description -n %{libname}
Shared libraries for %{name}

%package -n	%{develname}
Summary:	Development library and header files for the %{name} library
Group:		Development/C
Requires:	%{libname} = %{epoch}:%{version}-%{release}
Provides:	%{name}-devel = %{epoch}:%{version}-%{release}
Provides:	lib%{name}-devel = %{epoch}:%{version}-%{release}
Obsoletes:	%{mklibname c-icap 0 -d}

%description -n %{develname}
This package contains the static %{libname} library and its header
files.

%package	server
Summary:	An ICAP server coded in C
Group:          System/Servers
Requires:	%{name}-modules = %{epoch}:%{version}-%{release}
Requires:	file webserver clamav clamd
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper

%description	server
An ICAP server coded in C

%package	client
Summary:	An ICAP client coded in C
Group:          System/Servers

%description	client
An ICAP client coded in C

%package	modules
Summary:	Modules for the c-icap-server
Group:          System/Servers

%description	modules
Modules for the c-icap-server

%prep

%setup -q -n c_icap-%{version}
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p0

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;

for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

# strip away annoying ^M
find -type f | grep -v "\.gif" | grep -v "\.png" | grep -v "\.jpg" | xargs dos2unix -U

chmod 644 AUTHORS COPYING TODO

cp %{SOURCE1} icapd.init
cp %{SOURCE2} icapd.sysconfig
cp %{SOURCE3} icapd.logrotate

%build
export WANT_AUTOCONF_2_5=1
libtoolize --copy --force; aclocal-1.7; autoconf; automake-1.7 --foreign --add-missing --copy

%configure2_5x \
    --enable-static \
    --enable-shared \
    --with-clamav=%{_prefix} \
    --with-perl=%{_bindir}/perl

%make

%install
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

%makeinstall_std

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_var}/log/icapd
install -d %{buildroot}%{_var}/run/icapd
install -d %{buildroot}%{_var}/www/cgi-bin

mv %{buildroot}%{_bindir}/c-icap %{buildroot}%{_sbindir}/icapd

install -m0755 icapd.init %{buildroot}%{_initrddir}/icapd
install -m0644 icapd.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/icapd
install -m0644 icapd.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/icapd
install -m0755 contrib/get_file.pl %{buildroot}%{_var}/www/cgi-bin/get_file.pl

# nuke rpath
chrpath -d %{buildroot}%{_sbindir}/*
chrpath -d %{buildroot}%{_bindir}/*

touch %{buildroot}%{_var}/log/icapd/server.log
touch %{buildroot}%{_var}/log/icapd/access.log

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%pre server
%_pre_useradd icapd %{_localstatedir}/lib/icapd /bin/sh

%post server
%_post_service icapd
%create_ghostfile %{_var}/log/icapd/server.log icapd icapd 0644
%create_ghostfile %{_var}/log/icapd/access.log icapd icapd 0644

%preun server
%_preun_service icapd

%postun server
%_postun_userdel icapd

%clean
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

%files server
%defattr(-,root,root)
%doc AUTHORS COPYING TODO
%attr(0755,root,root) %{_initrddir}/icapd
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/c-icap.conf
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/c-icap.magic
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/sysconfig/icapd
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/logrotate.d/icapd
%attr(0755,root,root) %{_sbindir}/icapd
%attr(0755,root,root) %{_var}/www/cgi-bin/get_file.pl
%attr(0755,icapd,icapd) %dir %{_var}/log/icapd
%attr(0755,icapd,icapd) %dir %{_var}/run/icapd
%ghost %attr(0644,icapd,icapd) %{_var}/log/icapd/server.log
%ghost %attr(0644,icapd,icapd) %{_var}/log/icapd/access.log

%files client
%defattr(-,root,root)
%attr(0755,root,root) %{_bindir}/icap-client
%attr(0755,root,root) %{_bindir}/icap-stretch

%files modules
%defattr(-,root,root)
%dir %{_libdir}/c_icap
%attr(0755,root,root) %{_libdir}/c_icap/*.so

%files -n %{libname}
%defattr(-,root,root)
%attr(0755,root,root) %{_libdir}/*.so.*

%files -n %{develname}
%defattr(-,root,root)
%dir %{_includedir}/c_icap
%attr(0644,root,root) %{_includedir}/c_icap/*
%attr(0644,root,root) %{_libdir}/c_icap/*.a
%attr(0644,root,root) %{_libdir}/c_icap/*.la
%attr(0644,root,root) %{_libdir}/*.a
%attr(0755,root,root) %{_libdir}/*.so
%attr(0644,root,root) %{_libdir}/*.la
