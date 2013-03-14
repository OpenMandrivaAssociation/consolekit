%define pkgname	ConsoleKit
%define major	0
%define libname %mklibname ck-connector %{major}
%define devname %mklibname -d ck-connector

%define git_url git://anongit.freedesktop.org/ConsoleKit
%define _with_systemd 1

Summary:	System daemon for tracking users, sessions and seats
Name:		consolekit
Version:	0.4.5
Release:	ZED'S DEAD BABY (OBSOLETED BY SYSTEMD)
License:	GPLv2+
Group:		System/Libraries
Url:		http://www.freedesktop.org/wiki/Software/ConsoleKit
Source0:	http://www.freedesktop.org/software/ConsoleKit/dist/%{pkgname}-%{version}.tar.bz2
# (blino) daemonize only after ConsoleKit is available
#         or "activation" from clients will fail since D-Bus requires
#         the service name to be acquired before the daemon helper exits
Patch3:		ConsoleKit-0.4.2-daemonize_later.patch

BuildRequires:	docbook-dtd412-xml
BuildRequires:	xmlto
BuildRequires:	pam-devel
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(dbus-glib-1)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(polkit-agent-1)
BuildRequires:	pkgconfig(x11)
%if %{_with_systemd}
BuildRequires:	systemd-units
%endif
Requires(post,preun):	chkconfig
Requires:	pam
Provides:	should-restart = system
Conflicts:	%{libname} < 0.4.5-3

%description
ConsoleKit is a system daemon for tracking what users are logged
into the system and how they interact with the computer (e.g.
which keyboard and mouse they use).

It provides asynchronous notification via the system message bus and 
a PAM module for interacting with ConsoleKit.

%package x11
Summary:	X11-requiring add-ons for ConsoleKit
Group:		System/Libraries
Requires:	%{name} = %{version}-%{release}

%description x11
ConsoleKit contains some tools that require Xlib to be installed,
those are in this separate package so server systems need not install
X. Applications (such as xorg-x11-xinit) and login managers (such as
gdm) that need to register their X sessions with ConsoleKit needs to
have a requires for this package.

%package -n %{libname}
Summary:	ConsoleKit libraries
Group:		System/Libraries
License:	MIT
Obsoletes:	%{_lib}consolekit0 < 0.4.5-5

%description -n %{libname}
This package containes the shared library for ConsoleKit.

%package -n %{devname}
Summary:	Development library and headers for ConsoleKit
Group:		Development/C
License:	MIT
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{_lib}consolekit-devel < 0.4.5-5

%description -n %{devname}
Headers, library and API docs for ConsoleKit

%prep
%setup -qn %{pkgname}-%{version}
%apply_patches

%build
%configure2_5x \
	--disable-static \
	--localstatedir=%{_var} \
	--with-pid-file=%{_var}/run/console-kit-daemon.pid \
	--enable-pam-module \
	--with-pam-module-dir=/%{_lib}/security \
%if !%{_with_systemd}
	--without-systemdsystemunitdir \
%else
	--with-systemdsystemunitdir=%{_unitdir} \
%endif
	--enable-docbook-docs

%make

%install
%makeinstall_std

rm -rf %{buildroot}/%{_datadir}/doc/ConsoleKit
# make sure we don't package a history log
rm -f %{buildroot}/%{_var}/log/ConsoleKit/history

%pre
# remove obsolete ConsoleKit initscript
if [ -f %{_sysconfdir}/rc.d/init.d/consolekit ]; then 
    /sbin/service consolekit stop > /dev/null 2>/dev/null || :
    /sbin/chkconfig --del consolekit
fi

%post
if [ -f /var/log/ConsoleKit/history ]; then
    chmod a+r /var/log/ConsoleKit/history
fi

%files
%doc README AUTHORS NEWS COPYING
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/*
%{_sbindir}/console-kit-daemon
%{_sbindir}/ck-log-system-start
%{_sbindir}/ck-log-system-restart
%{_sbindir}/ck-log-system-stop
%{_bindir}/ck-history
%{_bindir}/ck-list-sessions
%{_bindir}/ck-launch-session
%config(noreplace) %{_sysconfdir}/ConsoleKit
/%{_lib}/security/*.so
%{_prefix}/lib/ConsoleKit
%{_datadir}/polkit-1/actions/*
%{_datadir}/dbus-1/system-services/*
%attr(755,root,root) %{_var}/log/ConsoleKit
%attr(750,root,root) %{_var}/run/ConsoleKit
%if %{_with_systemd}
%{_unitdir}/console-kit-daemon.service
%{_unitdir}/console-kit-log-system-start.service
%{_unitdir}/console-kit-log-system-stop.service
%{_unitdir}/console-kit-log-system-restart.service
%{_unitdir}/basic.target.wants/console-kit-log-system-start.service
%{_unitdir}/halt.target.wants/console-kit-log-system-stop.service
%{_unitdir}/kexec.target.wants/console-kit-log-system-restart.service
%{_unitdir}/poweroff.target.wants/console-kit-log-system-stop.service
%{_unitdir}/reboot.target.wants/console-kit-log-system-restart.service
%endif
%{_mandir}/man8/pam_ck_connector.8.*

%files x11
%{_libexecdir}/ck-*

%files -n %{libname}
%{_libdir}/libck-connector.so.%{major}*

%files -n %{devname}
%doc doc/dbus/ConsoleKit.html
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*
%{_datadir}/dbus-1/interfaces/*

