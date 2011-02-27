%define glib2_version           2.7.0
%define dbus_version            0.90
%define dbus_glib_version       0.70

%define lib_major 0
%define lib_name %mklibname consolekit %lib_major
%define lib_name_devel %mklibname -d consolekit 

%define pkgname ConsoleKit

%define git_url git://anongit.freedesktop.org/ConsoleKit

%define _with_systemd 1

Summary: System daemon for tracking users, sessions and seats
Name: consolekit
Version: 0.4.4
Release: %mkrel 1
License: GPLv2+
Group: System/Libraries
URL: http://www.freedesktop.org/wiki/Software/ConsoleKit
Source0: http://www.freedesktop.org/software/ConsoleKit/dist/%{pkgname}-%{version}.tar.bz2
# (blino) daemonize only after ConsoleKit is available
#         or "activation" from clients will fail since D-Bus requires
#         the service name to be acquired before the daemon helper exits
Patch3: ConsoleKit-0.4.2-daemonize_later.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: dbus-devel  >= %{dbus_version}
BuildRequires: dbus-glib-devel >= %{dbus_glib_version}
BuildRequires: polkit-1-devel
BuildRequires: pam-devel
BuildRequires: libx11-devel
BuildRequires: xmlto
BuildRequires: docbook-dtd412-xml
%if %{_with_systemd}
BuildRequires:	systemd-units
%endif

Requires(post): chkconfig
Requires(preun): chkconfig
Provides:   should-restart = system

Provides: %{pkgname} = %{version}-%{release}

%description 
ConsoleKit is a system daemon for tracking what users are logged
into the system and how they interact with the computer (e.g.
which keyboard and mouse they use).

It provides asynchronous notification via the system message bus.

%package x11
Summary: X11-requiring add-ons for ConsoleKit
Group: System/Libraries
Requires: %{name} = %{version}
License: GPLv2+

%description x11
ConsoleKit contains some tools that require Xlib to be installed,
those are in this separate package so server systems need not install
X. Applications (such as xorg-x11-xinit) and login managers (such as
gdm) that need to register their X sessions with ConsoleKit needs to
have a Requires: for this package.

%package -n %{lib_name}
Summary: ConsoleKit libraries
Group: System/Libraries
Requires: pam
Requires: %{name} >= %{version}
Provides: %{_lib}%{name} = %{version}-%{release}
License: MIT

%description -n %{lib_name}
Libraries and a PAM module for interacting with ConsoleKit.

%package -n %{lib_name_devel}
Summary: Development libraries and headers for ConsoleKit
Group: Development/C
Requires: %{lib_name} = %{version}
Provides: %{name}-devel = %{version}-%{release}
Provides: %{pkgname}-devel = %{version}-%{release}
License: MIT

%description -n %{lib_name_devel}
Headers, libraries and API docs for ConsoleKit

%prep
%setup -q -n %{pkgname}-%{version}
%apply_patches

%build
%configure2_5x --localstatedir=%{_var} \
		--with-pid-file=%{_var}/run/console-kit-daemon.pid \
		--enable-pam-module \
		--with-pam-module-dir=/%{_lib}/security \
%if !%{_with_systemd}
		--without-systemdsystemunitdir \
%endif
		--enable-docbook-docs 

%make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

rm -f $RPM_BUILD_ROOT%{_libdir}/*.{a,la}
rm -f $RPM_BUILD_ROOT/%{_lib}/security/*.{a,la}
rm -rf $RPM_BUILD_ROOT/%{_datadir}/doc/ConsoleKit
# make sure we don't package a history log
rm -f $RPM_BUILD_ROOT/%{_var}/log/ConsoleKit/history

%clean
rm -rf $RPM_BUILD_ROOT

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


%if %mdkversion < 200900
%post -n %{lib_name} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{lib_name} -p /sbin/ldconfig
%endif

%files
%defattr(-,root,root,-)
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
%{_prefix}/lib/ConsoleKit
%{_datadir}/polkit-1/actions/*
%{_datadir}/dbus-1/system-services/*
%attr(755,root,root) %{_var}/log/ConsoleKit
%attr(750,root,root) %{_var}/run/ConsoleKit
%if %{_with_systemd}
/lib/systemd
/lib/systemd/system/console-kit-daemon.service
/lib/systemd/system/console-kit-log-system-start.service
/lib/systemd/system/console-kit-log-system-stop.service
/lib/systemd/system/console-kit-log-system-restart.service
/lib/systemd/system/basic.target.wants/console-kit-log-system-start.service
/lib/systemd/system/halt.target.wants/console-kit-log-system-stop.service
/lib/systemd/system/poweroff.target.wants/console-kit-log-system-stop.service
/lib/systemd/system/reboot.target.wants/console-kit-log-system-restart.service
%endif

%files x11
%defattr(-,root,root,-)
%{_libexecdir}/ck-*

%files -n %{lib_name}
%defattr(-,root,root,-)
%{_libdir}/lib*.so.*
/%{_lib}/security/*.so
%{_mandir}/man8/pam_ck_connector.8.*

%files -n %{lib_name_devel}
%defattr(-,root,root,-)
%doc doc/dbus/ConsoleKit.html
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*
%{_datadir}/dbus-1/interfaces/*

