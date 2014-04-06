%define major 2
%define libname %mklibname c-icap %{major}
%define develname %mklibname c-icap -d

%define epoch 4

Summary:	An ICAP server coded in C
Name:		c-icap
Version:	0.2.3
Release:	4
License:	GPL
Group:		System/Servers
URL:		http://sourceforge.net/projects/c-icap/
Source0:	http://prdownloads.sourceforge.net/c-icap/c_icap-%{version}.tar.gz
Source1:	c-icap.service
Source2:	icapd.sysconfig
Source3:	icapd.logrotate
Source4:	c-icap-tmpfiles.conf
Patch0:		c_icap-mdv_conf.diff
Patch1:		c_icap-makefile.patch
Patch2:		c_icap-030606-perllib_fix.patch
Patch3:		fix_lookuptable.patch
Patch4:		c_icap-domain_strip.diff
BuildRequires:	clamav-devel
BuildRequires:	chrpath
BuildRequires:	dos2unix
BuildRequires:	automake
BuildRequires:	autoconf
BuildRequires:	perl-devel
BuildRequires:	pkgconfig(libcurl)
BuildRequires:	bzip2-devel
BuildRequires:	pkgconfig(libidn)
BuildRequires:	gmp-devel
BuildRequires:	pkgconfig(openssl)
BuildRequires:  doxygen
BuildRequires:  db-devel
BuildRequires:  file
BuildRequires:  openldap-devel
Epoch:		%{epoch}
Requires(pre,post):	rpm-helper
Requires(postun,preun):	rpm-helper

%description
c-icap is an implementation of an ICAP server. It can be used with HTTP 
proxies that support the ICAP protocol to implement content adaptation 
and filtering services

Most of the commercial HTTP proxies must support the ICAP protocol. The 
open source Squid 3.x proxy server supports it

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
Requires:	file webserver
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Suggests:	c-icap-modules-extra
%description	server
An ICAP server coded in C.

%package	client
Summary:	An ICAP client coded in C
Group:          System/Servers

%description	client
An ICAP client coded in C.

%package	modules
Summary:	Modules for the c-icap-server
Group:          System/Servers

%description	modules
Modules for the c-icap-server.

%prep

%setup -q -n c_icap-%{version}
%patch0 -p0
%patch1 -p0
%patch2 -p0
#patch3 -p0
%patch4 -p0 -b domain_strip

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;

for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

# strip away annoying ^M
# find -type f | grep -v "\.gif" | grep -v "\.png" | grep -v "\.jpg" | xargs dos2unix -U
# find -type f -exec dos2unix --skipbin -U -n {} {} \;
chmod 644 AUTHORS COPYING TODO

cp %{SOURCE2} icapd.sysconfig
cp %{SOURCE3} icapd.logrotate

%build
export WANT_AUTOCONF_2_5=1
libtoolize --copy --force; aclocal; autoconf; automake --foreign --add-missing --copy

export LIBS="-lpthread -ldl"
export ICAP_DIR=`pwd`

%configure2_5x \
    --disable-static \
    --enable-shared \
    --with-perl=%{_bindir}/perl \
    --with-ldap

make

%install
%makeinstall_std CONFIGDIR=%{_sysconfdir}/icapd
install -d -m0755 %{buildroot}%{_sysconfdir}/sysconfig
install -d -m0755 %{buildroot}%{_sysconfdir}/logrotate.d
install -d -m0755 %{buildroot}%{_sbindir}
install -d -m0755 %{buildroot}%{_var}/log/icapd
install -d -m0755 %{buildroot}%{_var}/www/cgi-bin

mv %{buildroot}%{_bindir}/c-icap %{buildroot}%{_sbindir}/icapd
install -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/icapd.service
install -m0644 icapd.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/icapd
install -m0644 icapd.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/icapd
install -m0755 contrib/get_file.pl %{buildroot}%{_var}/www/cgi-bin/get_file.pl
install -D -p -m 0644 %{SOURCE4} %{buildroot}%{_tmpfilesdir}/%{name}.conf

# nuke rpath
chrpath -d %{buildroot}%{_sbindir}/*

#chrpath -d %{buildroot}%{_bindir}/c-icap
chrpath -d %{buildroot}%{_bindir}/c-icap-client
#chrpath -d %{buildroot}%{_bindir}/c-icap-mkbdb
chrpath -d %{buildroot}%{_bindir}/c-icap-stretch

#for l in %{buildroot}%{_bindir}/* ; do
# file $l |grep "not stripped" 
# if [ $? -eq 0 ]; then
#  chrpath -d $l
#  continue
# else
#  echo "not need to strip"
#  continue#
# fi
#done

touch %{buildroot}%{_var}/log/icapd/server.log
touch %{buildroot}%{_var}/log/icapd/access.log

# cleanup
rm -f %{buildroot}%{_libdir}/c_icap/*.*a
rm -f %{buildroot}%{_libdir}/*.*a

%pre server
%_pre_useradd icapd /var/lib/icapd /bin/sh

%post server
%_post_service icapd
#%create_ghostfile %{_var}/log/icapd/server.log icapd icapd 0644
#%create_ghostfile %{_var}/log/icapd/access.log icapd icapd 0644

%preun server
%_preun_service icapd

%postun server
%_postun_userdel icapd

%files server
%doc AUTHORS COPYING TODO
%{_unitdir}/icapd.service
%{_tmpfilesdir}/%{name}.conf
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/icapd/c-icap.conf
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/icapd/c-icap.magic
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/sysconfig/icapd
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/logrotate.d/icapd
%attr(0755,root,root) %{_sbindir}/icapd
%attr(0755,root,root) %{_var}/www/cgi-bin/get_file.pl
%attr(0755,icapd,icapd) %dir %{_var}/log/icapd
%attr(0755,icapd,icapd) %dir %{_var}/run/icapd
%ghost %attr(0644,icapd,icapd) %{_var}/log/icapd/server.log
%ghost %attr(0644,icapd,icapd) %{_var}/log/icapd/access.log
%attr(0755,root,root) %{_mandir}/man8/c-icap.8.*

%files client
%attr(0755,root,root) %{_bindir}/c-icap-client
%attr(0755,root,root) %{_bindir}/c-icap-stretch
%attr(0755,root,root) %{_bindir}/c-icap-mkbdb
%attr(0755,root,root) %{_mandir}/man8/c-icap-client.8.*
%attr(0755,root,root) %{_mandir}/man8/c-icap-mkbdb.8.*
%attr(0755,root,root) %{_mandir}/man8/c-icap-stretch.8.*



%files modules
%dir %{_libdir}/c_icap
%attr(0755,root,root) %{_libdir}/c_icap/*.so

%files -n %{libname}
%attr(0755,root,root) %{_libdir}/*.so.%{major}*

%files -n %{develname}
%dir %{_includedir}/c_icap
%attr(0644,root,root) %{_includedir}/c_icap/*
%attr(0755,root,root) %{_libdir}/*.so
%attr(0755,root,root) %{_bindir}/c-icap-config
%attr(0755,root,root) %{_bindir}/c-icap-libicapapi-config
%attr(0755,root,root) %{_mandir}/man8/c-icap-config.8.*
%attr(0755,root,root) %{_mandir}/man8/c-icap-libicapapi-config.8.*
