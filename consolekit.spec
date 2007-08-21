%define glib2_version           2.6.0
%define dbus_version            0.90
%define dbus_glib_version       0.70

%define lib_major 0
%define lib_name %mklibname consolekit %lib_major
%define lib_name_devel %mklibname -d consolekit 

%define pkgname ConsoleKit

Summary: System daemon for tracking users, sessions and seats
Name: consolekit
Version: 0.2.1
Release: %mkrel 4
License: GPL
Group: System/Libraries
URL: http://consolekit.freedesktop.org
Source0: http://people.freedesktop.org/~mccann/dist/%{pkgname}-%{version}.tar.gz
# (fc) add lsb header
Patch0: ConsoleKit-0.2.1-lsb.patch
# (fc) 0.2.1-1mdv fix build with old inotify header
Patch1: ConsoleKit-0.2.1-header.patch
# (fc) 0.2.1-3mdv fix initscript order
Patch2: ConsoleKit-0.2.1-order.patch
# (fc) 0.2.1-4mdv remove gdm specific configuration, it is in gdm package now (Mdv bug #32571)
Patch3: ConsoleKit-0.2.1-gdm.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires(pre): rpm-helper
Requires(preun): rpm-helper

BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: dbus-devel  >= %{dbus_version}
BuildRequires: dbus-glib-devel >= %{dbus_glib_version}
BuildRequires: pam-devel
BuildRequires: X11-devel
BuildRequires: xmlto

Requires(post): chkconfig
Requires(preun): chkconfig

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

%description -n %{lib_name}
Libraries and a PAM module for interacting with ConsoleKit.

%package -n %{lib_name_devel}
Summary: Development libraries and headers for ConsoleKit
Group: Development/C
Requires: %{lib_name} = %{version}
Provides: %{name}-devel = %{version}-%{release}
Provides: %{pkgname}-devel = %{version}-%{release}

%description -n %{lib_name_devel}
Headers, libraries and API docs for ConsoleKit

%prep
%setup -q -n %{pkgname}-%{version}
%patch0 -p1 -b .lsb
%patch1 -p1 -b .header
%patch2 -p1 -b .order
%patch3 -p1 -b .gdm

%build
%configure2_5x --localstatedir=%{_var} --with-pid-file=%{_var}/run/console-kit-daemon.pid --enable-pam-module --with-pam-module-dir=/%{_lib}/security --enable-docbook-docs 

#parallel build is broken
make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

#rename to lowercase
mv $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/ConsoleKit $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/consolekit 

rm -f $RPM_BUILD_ROOT%{_libdir}/*.{a,la}
rm -f $RPM_BUILD_ROOT/%{_lib}/security/*.{a,la}
rm -rf $RPM_BUILD_ROOT/%{_datadir}/doc/ConsoleKit

%clean
rm -rf $RPM_BUILD_ROOT

%post
%_post_service consolekit
/sbin/chkconfig consolekit resetpriorities

%preun
%_preun_service consolekit

%post -n %{lib_name} -p /sbin/ldconfig

%postun -n %{lib_name} -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc README AUTHORS NEWS COPYING

%config(noreplace) %{_sysconfdir}/dbus-1/system.d/*
%{_sysconfdir}/rc.d/init.d/consolekit
%{_sbindir}/console-kit-daemon
%{_bindir}/ck-list-sessions

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
%doc doc/ConsoleKit.html
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*
%{_includedir}/*

