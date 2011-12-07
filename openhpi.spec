Summary: Hardware Platform Interface library and tools
Name: openhpi
Version: 2.14.1
Release: 3%{?dist}
License: BSD
Group: System Environment/Base
URL: http://www.openhpi.org
Source0: http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
Source1: %{name}.initd
Source2: %{name}.sysconfig
# https://sourceforge.net/tracker/?func=detail&aid=2932689&group_id=71730&atid=532251
Patch0: openhpi-2.14.1-fumi-type.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: libsysfs-devel, net-snmp-devel, OpenIPMI-devel, glib2-devel
BuildRequires: libtool-ltdl-devel, openssl-devel, ncurses-devel
BuildRequires: libxml2-devel, docbook-utils, libuuid-devel
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service

%description
OpenHPI is an open source project created with the intent of providing an
implementation of the SA Forum's Hardware Platform Interface (HPI). HPI
provides an abstracted interface to managing computer hardware, typically for
chassis and rack based servers. HPI includes resource modeling; access to and
control over sensor, control, watchdog, and inventory data associated with
resources; abstracted System Event Log interfaces; hardware events and alerts;
and a managed hotswap interface.

OpenHPI provides a modular mechanism for adding new hardware and device support
easily. Many plugins exist in the OpenHPI source tree to provide access to
various types of hardware. This includes, but is not limited to, IPMI based
servers, Blade Center, and machines which export data via sysfs.


%package libs
Group: System Environment/Libraries
Summary: The system libraries for the openhpi project
Obsoletes: %{name} < 2.10.2-1

%description libs
The system libraries for the openhpi project.


%package devel
Group: Development/Libraries
Summary: The development environment for the openhpi project
Requires: %{name}-libs = %{version}-%{release}
Requires: glib2-devel, pkgconfig

%description devel
The development libraries and header files for the openhpi project.


%prep
%setup -q
%patch0 -p1 -b .fumi-type

# fix permissions
chmod a-x plugins/simulator/*.[ch]
chmod a-x clients/*.[ch]


%build
export CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"
%configure --disable-static

# Don't use rpath!
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{?_smp_mflags}


%install
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
mkdir -p $RPM_BUILD_ROOT%{_initddir}
mkdir -p -m1777 $RPM_BUILD_ROOT%{_var}/lib/%{name}
make install DESTDIR=$RPM_BUILD_ROOT

rm -f $RPM_BUILD_ROOT%{_sysconfdir}/init.d/openhpid
install -p -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_initddir}/openhpid
install -p -m 755 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/openhpid

rm -rf $RPM_BUILD_ROOT/%{_libdir}/*.la
rm -rf $RPM_BUILD_ROOT/%{_libdir}/%{name}/*.la

# fix perms for generated docs
chmod 0644 docs/hld/openhpi-manual/*.html


%check
make check


%clean
rm -rf $RPM_BUILD_ROOT


%post
/sbin/chkconfig --add openhpid

%preun
if [ $1 = 0 ] ; then
    /sbin/service openhpid stop >/dev/null 2>&1
    /sbin/chkconfig --del openhpid
fi

%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service openhpid condrestart >/dev/null 2>&1
fi

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc COPYING README README.daemon docs/hld/openhpi-manual openhpi.conf.example
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}/%{name}client.conf
%{_initddir}/openhpid
%config(noreplace) %{_sysconfdir}/sysconfig/openhpid
%attr(1777,root,root) %{_var}/lib/%{name}
%{_bindir}/*
%{_sbindir}/*
%{_libdir}/%{name}
%{_mandir}/man1/*
%{_mandir}/man7/*
%{_mandir}/man8/*

%files libs
%defattr(-,root,root,-)
%{_libdir}/*.so.*

%files devel
%defattr(-,root,root,-)
%doc COPYING
%{_libdir}/*.so
%{_includedir}/%{name}
%{_libdir}/pkgconfig/*.pc


%changelog
* Tue Mar  9 2010 Dan Horák <dhorak@redhat.com> - 2.14.1-3
- switched to new initscript
- Related: #543948

* Fri Jan 15 2010 Dan Horák <dan[at]danny.cz> - 2.14.1-2
- added fix for inconsistent SaHpi.h
- Related: #459522

* Wed Nov 25 2009 Dan Horák <dan[at]danny.cz> - 2.14.1-1
- updated to bug fix release 2.14.1

* Fri Oct  9 2009 Dan Horák <dan[at]danny.cz> - 2.14.0-6
- rebuilt with net-snmp 5.5

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 2.14.0-5
- rebuilt with new openssl

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.14.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 14 2009 Dan Horak <dan[at]danny.cz> - 2.14.0-3
- add BR: libuuid-devel

* Fri Apr 17 2009 Dan Horak <dan[at]danny.cz> - 2.14.0-2
- use upstream default config
- libtoolize/autoreconf is not needed

* Fri Apr 17 2009 Dan Horak <dan[at]danny.cz> - 2.14.0-1
- update to 2.14.0

* Wed Feb 25 2009 Dan Horak <dan[at]danny.cz> - 2.13.3-2
- fix ppc/ppc64 builds

* Wed Feb 25 2009 Dan Horak <dan[at]danny.cz> - 2.13.3-1
- update to 2.13.3

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> - 2.13.1-3
- rebuild with new openssl

* Tue Nov 25 2008 Dan Horak <dan[at]danny.cz> - 2.13.1-2
- shorten Summary

* Thu Nov 20 2008 Dan Horak <dan[at]danny.cz> - 2.13.1-1
- update to 2.13.1

* Mon Nov 17 2008 Dan Horak <dan[at]danny.cz> - 2.12.0-2
- rebuild for new libtool

* Sat Jul 26 2008 Dan Horak <dan[at]danny.cz> - 2.12.0-1
- update to 2.12.0

* Thu Jun 27 2008 Dan Horak <dan[at]danny.cz> - 2.11.3-1
- update to 2.11.3

* Thu Apr 18 2008 Dan Horak <dan[at]danny.cz> - 2.10.2-2
- enable the sysfs plugin
- add missing R: for -devel subpackage

* Thu Mar 13 2008 Dan Horak <dan[at]danny.cz> - 2.10.2-1
- update to 2.10.2
- spec file and patch cleanup

* Thu Feb 28 2008 Phil Knirsch <pknirsch@redhat.com> - 2.10.1-3
- Removed incorrect patch for IBM BC snmp_bc plugin
- Fixed GCC 4.3 rebuild problems

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.10.1-2
- Autorebuild for GCC 4.3

* Wed Dec 05 2007 Phil Knirsch <pknirsch@redhat.com> - 2.10.1-1
- Updated to openhpi-2.10.1
- Bump release and rebuild due to new openssl

* Thu Aug 23 2007 Phil Knirsch <pknirsch@redhat.com> - 2.8.1-5
- Bump release and rebuild because of PPC issues
- Fix rebuild problems due to new glibc open macro

* Fri Jul 20 2007 Phil Knirsch <pknirsch@redhat.com> - 2.8.1-4
- Fix for hpipower segfaulting when using -b option out of range (#247279)

* Tue Jul 17 2007 Phil Knirsch <pknirsch@redhat.com> - 2.8.1-3
- Fixed a bug where the snmp_bc plugin didn't work in IBM BC (#247280)

* Mon Jun 04 2007 Phil Knirsch <pknirsch@redhat.com> - 2.8.1-2.fc7
- Fixed missing e2fsprogs-devel and openssl-devel build requires

* Fri Mar 30 2007 Phil Knirsch <pknirsch@redhat.com> - 2.8.1-1.fc7
- Update to openhpi-2.8.1

* Thu Feb 08 2007 Phil Knirsch <pknirsch@redhat.com> - 2.8.0-3.fc7
- Fixed some silly bugs in the specfile

* Wed Feb 07 2007 Phil Knirsch <pknirsch@redhat.com> - 2.8.0-2.fc7
- Bump and rebuild.

* Tue Feb 06 2007 Phil Knirsch <pknirsch@redhat.com> - 2.8.0-1.fc7
- Update to openhpi-2.8.0

* Tue Nov 28 2006 Phil Knirsch <pknirsch@redhat.com> - 2.4.1-7.fc7
- Rebuilt due to new net-snmp-5.4
- Small specfile updates

* Fri Sep 29 2006 Phil Knirsch <pknirsch@redhat.com> - 2.4.1-6
- Fixed file conflicts for openhpi-switcher (#205226)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.4.1-5.1
- rebuild

* Mon Jul 10 2006 Phil Knirsch <pknirsch@redhat.com> - 2.4.1-5
- Had to disable sysfs support due to new libsysfs and incompatible API.
- Added missing ncurses-devel buildrequires

* Wed Jun 07 2006 Phil Knirsch <pknirsch@redhat.com> - 2.4.1-4
- Rebuilt with final memset patch
- Added missing pkgconfig buildprereq (#191935)

* Fri May 26 2006 Radek Vokal <rvokal@redhat.com> - 2.4.1-2
- rebuilt for new libnetsnmp and net-snmp-config changes

* Wed May 24 2006 Phil Knirsch <pknirsch@redhat.com> - 2.4.1-1
- Fixed buggy use of memset throughout the code
- Made the package build and install properly

* Fri May 19 2006 Phil Knirsch <pknirsch@redhat.com>
- Added missing glib2-devel build prereq (#191935)
- Update to latest stable version openhpi-2.4.1

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.2.1-4.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.2.1-4.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Jan  9 2006 Peter Jones <pjones@redhat.com> 2.2.1-4
- Don't use -Werror, it doesn't build with that on ppc64 currently.

* Mon Jan 06 2006 Jesse Keating <jkeating@redhat.com> 2.2.1-3
- Fix to not use stict-aliasing.

* Wed Jan 04 2006 Radek Vokal <rvokal@redhat.com> 2.2.1-2
- Rebuilt against new libnetsnmp

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Nov 11 2005 Phil Knirsch <pknirsch@redhat.com> 2.2.1-1
- Update to stable openhpi-2.2.1

* Wed Nov 09 2005 Phil Knirsch <pknirsch@redhat.com> 2.0.3-5
- Rebuilt to link against latest openssl lib.

* Mon Nov 07 2005 Phil Knirsch <pknirsch@redhat.com> 2.0.3-4
- Added the openhpi config file
- Added missing /var/lib/openhpi dir with proper rights
- Added a few missing BuildPreReqs

* Thu Nov 03 2005 Phil Knirsch <pknirsch@redhat.com> 2.0.3-3
- Rebuild against new net-snmp libs

* Wed Mar 30 2005 Phil Knirsch <pknirsch@redhat.com> 2.0.3-1
- Moved the pkgconfig files to the devel package (#152507)
- Update to openhpi-2.0.3
- Had to manually disable ipmi support for now until openhpi builds correctly
  against it again
- Dropped net-snmp-config patch, not needed anymore

* Thu Mar 17 2005 Phil Knirsch <pknirsch@redhat.com> 1.9.2-5
- Fixed gcc4 rebuild problems

* Wed Mar 02 2005 Phil Knirsch <pknirsch@redhat.com> 1.9.2-4
- bump release and rebuild with gcc 4

* Mon Feb 14 2005 Phil Knirsch <pknirsch@redhat.com> 1.9.2-3
- Rebuilt for new rpm-4.4

* Mon Dec 20 2004 Phil Knirsch <pknirsch@redhat.com> 1.9.2-2
- Fixed overflow in plugins/sysfs/sysfs2hpi.c
- Fixed rebuild problem with latest net-snmp
- Removed is_simulator patch, not needed anymore

* Fri Nov 26 2004 Florian La Roche <laroche@redhat.com> 1.9.2-1
- update to 1.9.2

* Tue Nov 02 2004 Phil Knirsch <pknirsch@redhat.com> 1.9.1-1
- Added proper BuildRequires
- Drop ia64 for first build, something fishy with the compiler and warning.

* Tue Oct 26 2004 Phil Knirsch <pknirsch@redhat.com>
- Initial version
- Disable dummy plugin, doesn't compile
- Fix missing () in snmp_bc_session.c
