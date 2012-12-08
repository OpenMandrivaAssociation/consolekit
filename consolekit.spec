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
Version: 0.4.5
Release: %mkrel 2
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
%else
		--with-systemdsystemunitdir=/lib/systemd/system \
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
/lib/systemd/system/console-kit-daemon.service
/lib/systemd/system/console-kit-log-system-start.service
/lib/systemd/system/console-kit-log-system-stop.service
/lib/systemd/system/console-kit-log-system-restart.service
/lib/systemd/system/basic.target.wants/console-kit-log-system-start.service
/lib/systemd/system/halt.target.wants/console-kit-log-system-stop.service
/lib/systemd/system/poweroff.target.wants/console-kit-log-system-stop.service
/lib/systemd/system/reboot.target.wants/console-kit-log-system-restart.service
/lib/systemd/system/kexec.target.wants/console-kit-log-system-restart.service
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



%changelog
* Wed Feb 22 2012 abf
- The release updated by ABF

* Mon May 16 2011 Götz Waschk <waschk@mandriva.org> 0.4.5-1mdv2011.0
+ Revision: 675017
- update to new version 0.4.5

* Tue May 03 2011 Oden Eriksson <oeriksson@mandriva.com> 0.4.4-2
+ Revision: 663398
- mass rebuild

* Sun Feb 27 2011 Götz Waschk <waschk@mandriva.org> 0.4.4-1
+ Revision: 640407
- update to new version 0.4.4

* Tue Jan 18 2011 Eugeni Dodonov <eugeni@mandriva.com> 0.4.3-3
+ Revision: 631461
- Enable systemd support.

* Tue Nov 30 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 0.4.3-2mdv2011.0
+ Revision: 603985
- Replace BR X11-devel for libx11-devel
  This should save 75 packages when compiling on a clean chroot
  Build logs seem identical

* Fri Nov 26 2010 Götz Waschk <waschk@mandriva.org> 0.4.3-1mdv2011.0
+ Revision: 601484
- new version
- drop patch 4

* Thu Nov 18 2010 Eugeni Dodonov <eugeni@mandriva.com> 0.4.2-2mdv2011.0
+ Revision: 598764
- P4: fix console ownership after suspend.

* Mon Sep 27 2010 Götz Waschk <waschk@mandriva.org> 0.4.2-1mdv2011.0
+ Revision: 581225
- new version
- drop patches 1,2,4
- rediff patch 3

* Fri Dec 18 2009 Frederic Crozat <fcrozat@mandriva.com> 0.4.1-3mdv2010.1
+ Revision: 479971
- Patch4 : do not use daemon mode when activating through D-Bus (Mdv bug #56514)

* Thu Dec 17 2009 Olivier Blin <oblin@mandriva.com> 0.4.1-2mdv2010.1
+ Revision: 479764
- fix activation as D-Bus service

* Fri Sep 25 2009 Frederic Crozat <fcrozat@mandriva.com> 0.4.1-1mdv2010.0
+ Revision: 449056
- Release 0.4.1
- Regenerate patch1
- Remove unapplied upstream merged patches from repository

* Mon Aug 17 2009 Colin Guthrie <cguthrie@mandriva.org> 0.3.1-3mdv2010.0
+ Revision: 417131
- Disable the restructure until udev is officially patched for this change (patch written but not yet available)

* Sun Aug 16 2009 Colin Guthrie <cguthrie@mandriva.org> 0.3.1-2mdv2010.0
+ Revision: 416974
- Apply upstream fixes for various race conditions (pulseaudio related)
- Use %%apply_patches macro for simplicity

* Thu Aug 06 2009 Frederic Crozat <fcrozat@mandriva.com> 0.3.1-1mdv2010.0
+ Revision: 410857
- Fix buildrequires
- Release 0.3.1
- Remove patches 2, 3, 4, 5, 6, 7, 8 (merged upstream)
- Patch2 (Fedora): fix memleaks

* Wed Apr 08 2009 Frederic Crozat <fcrozat@mandriva.com> 0.3.0-5mdv2009.1
+ Revision: 365158
- Patches 2 to 7 : bug fixes from GIT
- Patch8 (vuntz): allow getsessions from Manager (needed by gnome-session) (fdo bug #20471)

* Tue Dec 30 2008 Oden Eriksson <oeriksson@mandriva.com> 0.3.0-4mdv2009.1
+ Revision: 321404
- fix build with -Werror=format-security (P1)

* Tue Sep 30 2008 Frederic Crozat <fcrozat@mandriva.com> 0.3.0-3mdv2009.0
+ Revision: 290127
- Patch0 (GIT): allow SetIdleHint

* Wed Aug 13 2008 Frederic Crozat <fcrozat@mandriva.com> 0.3.0-2mdv2009.0
+ Revision: 271412
- request system reboot on update

* Tue Aug 12 2008 Frederic Crozat <fcrozat@mandriva.com> 0.3.0-1mdv2009.0
+ Revision: 271191
- Fix build for x86-64
- Release 0.3.0

* Wed Jul 23 2008 Frederic Crozat <fcrozat@mandriva.com> 0.2.10-1mdv2009.0
+ Revision: 242531
- Release 0.2.10
- Patch0 (Fedora): return policykit result when not privileged

* Mon Jun 16 2008 Thierry Vignaud <tv@mandriva.org> 0.2.9-2mdv2009.0
+ Revision: 220510
- rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Mon Feb 18 2008 Frederic Crozat <fcrozat@mandriva.com> 0.2.9-1mdv2008.1
+ Revision: 170132
- Release 0.2.9

* Mon Feb 04 2008 Frederic Crozat <fcrozat@mandriva.com> 0.2.7-2mdv2008.1
+ Revision: 162382
- Unregister obsolete initscript in pre script, not preun

* Fri Feb 01 2008 Frederic Crozat <fcrozat@mandriva.com> 0.2.7-1mdv2008.1
+ Revision: 161061
- Release 0.2.7
- Release 0.2.6
- Remove patches 0, 1, 2 (no longer needed)

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Nov 19 2007 Frederic Crozat <fcrozat@mandriva.com> 0.2.3-3mdv2008.1
+ Revision: 110481
- Drop call to chkconfig resetpriorities, it was Fedora specific. Fixes Mdv bug #35650.

* Thu Oct 18 2007 Ademar de Souza Reis Jr <ademar@mandriva.com.br> 0.2.3-2mdv2008.1
+ Revision: 99981
- fix project URL
- remove trailing whitespace (cosmetic)

* Mon Oct 15 2007 Frederic Crozat <fcrozat@mandriva.com> 0.2.3-1mdv2008.1
+ Revision: 98581
- Release 0.2.3
- Remove patch3, merged upstream

* Tue Aug 21 2007 Frederic Crozat <fcrozat@mandriva.com> 0.2.1-4mdv2008.0
+ Revision: 68533
- Patch3: remove gdm configuration, move it to gdm package (Mdv bug #32571)

* Fri Aug 17 2007 Frederic Crozat <fcrozat@mandriva.com> 0.2.1-3mdv2008.0
+ Revision: 65112
- Patch2: fix initscript order (partially fix Mdv bug #32555)

* Wed Aug 01 2007 Frederic Crozat <fcrozat@mandriva.com> 0.2.1-2mdv2008.0
+ Revision: 57703
- Add provides on lib package

* Fri Jul 13 2007 Frederic Crozat <fcrozat@mandriva.com> 0.2.1-1mdv2008.0
+ Revision: 51844
-Fix bad macro usage
- Import consolekit

