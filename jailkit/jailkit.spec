# $Id: jailkit.spec 8843 2010-06-02 19:48:48Z shuff $
# Authority: dag

# Adds -z now to the linker flags
%global _hardened_build 1

Summary: Utilities to limit user accounts to specific files using chroot()
Name: jailkit
Version: 2.23
Release: 6%{?dist}
Epoch: 2
License: BSD & LGPL
Group: System Environment/Base
URL: http://olivier.sessink.nl/jailkit/

Source: http://olivier.sessink.nl/jailkit/jailkit-%{version}.tar.bz2
Source1: jailkit.service

#Source01: https://d.peegeepee.com/64979277BAFF2D4CB637AC3B291C63A6B78DFBA1.asc
#Source02: https://olivier.sessink.nl/jailkit/%{name}-%{version}.tar.bz2.sig


Patch1: jailkit-2.17-makefile.patch
Patch2: jailkit-2.23-nosetuid.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: binutils, gcc, make
BuildRequires: glibc-devel, libcap-devel
%if 0%{?rhel} > 6
BuildRequires:  systemd-devel systemd systemd-libs systemd-rpm-macros
%else
BuildRequires:  initscripts
%endif

%if 0%{?rhel} > 6
Requires(preun): systemd
Requires(postun): systemd
Requires(post): systemd
%else
Requires(preun): initscripts
Requires(postun): initscripts
Requires(post): initscripts
%endif




%if 0%{?fedora} > 28 || 0%{?rhel} > 7 && 0%{?rhel} <= 8
BuildRequires: python2
%else
BuildRequires: python
%endif

%description
Jailkit is a set of utilities to limit user accounts to specific files
using chroot() and or specific commands. Setting up a chroot shell,
a shell limited to some specific command, or a daemon inside a chroot
jail is a lot easier using these utilities.

Jailkit has been in use for a while on CVS servers (in a chroot and
limited to cvs), sftp/scp servers (both in a chroot and limited to
sftp/scp as well as not in a chroot but only limited to sftp/scp),
and also on general servers with accounts where the shell accounts
are in a chroot.



%prep
#%{?gpgverify:%{gpgverify} --keyring='%{SOURCE01}' --signature='%{SOURCE02}' --data='%{SOURCE}'}
%setup
%if 0%{?rhel} > 9
%patch -p0 -P1 -b .makefile
%patch -p1 -P2 -b .notsetuid
%else
%patch1 -p0 -b .makefile
%patch2 -p1 -b .notsetuid
%endif

%build
%if 0%{?fedora} > 28 || 0%{?rhel} > 7 && 0%{?rhel} <= 8
export PYTHONINTERPRETER="/usr/bin/python2"
%endif

%if 0%{?rhel} > 8
export PYTHONINTERPRETER="/usr/bin/python3"
%endif

%configure
%{__make} %{?_smp_mflags}


%install
%{__rm} -rf %{buildroot}
%{__make} install DESTDIR="%{buildroot}"
%if 0%{?rhel} < 7
%{__install} -Dp -m0755 extra/jailkit %{buildroot}%{_initrddir}/jailkit
%else
install -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/jailkit.service
%endif


%preun
%if 0%{?rhel} > 6
%systemd_preun jailkit.service
%else
if [ "$1" = "0" ] ; then
 /sbin/service jailkit stop >/dev/null 2>&1
fi
%endif



%post
if [ -w %{_sysconfdir}/shells ] && \
  [ "`grep %{_sbindir}/jk_chrootsh %{_sysconfdir}/shells`" == "" ]
then
  echo "%{_sbindir}/jk_chrootsh" >> %{_sysconfdir}/shells
fi
%if 0%{?rhel} > 6
%systemd_post jailkit.service
%else
/sbin/chkconfig --add jailkit
%endif



%postun
sed -i -e "/jk_chrootsh/d" %{_sysconfdir}/shells
%if 0%{?rhel} > 6
%systemd_postun jailkit.service
%else
/sbin/chkconfig --del jailkit
%endif



%clean
%{__rm} -rf %{buildroot}



%files
%defattr(-, root, root, 0755)
%doc %{_mandir}/man?/*
%config(noreplace) %{_sysconfdir}/jailkit/
%if 0%{?rhel} < 7
%{_initrddir}/jailkit
%else
%{_unitdir}/jailkit.service
%endif
%caps(cap_sys_chroot=ep) %{_bindir}/jk_uchroot
%caps(cap_sys_chroot=ep) %{_sbindir}/jk_chrootsh
%{_sbindir}/jk_lsh
%{_sbindir}/jk_chrootlaunch
%{_sbindir}/jk_socketd
%{_sbindir}/jk_check
%{_sbindir}/jk_cp
%{_sbindir}/jk_init
%{_sbindir}/jk_jailuser
%{_sbindir}/jk_list
%{_sbindir}/jk_update
%{_datadir}/jailkit/


%changelog
* Fri Feb 23 2024 Michael Seevogel <michael@michaelseevogel.de> - 2.23-6
- Update .spec file and add systemd unit file

* Mon Feb 19 2024 Michael Seevogel <michael@michaelseevogel.de> - 2.23-5
- Fixed jk_chrootsh

* Mon Feb 19 2024 Michael Seevogel <michael@michaelseevogel.de> - 2.23-4
- Fixed jk_chrootsh

* Wed Feb 09 2022 Michael Seevogel <michael@michaelseevogel.de> - 2.23-3
- Fixed Epoch

* Wed Feb 09 2022 Michael Seevogel <michael@michaelseevogel.de> - 2.23-2
- Fixed Jailkit executable permissions

* Tue Oct 05 2021 Michael Seevogel <michael@michaelseevogel.de> - 2.23-1
- Updated to release 2.23

* Tue May 04 2021 Michael Seevogel <michael@michaelseevogel.de> - 2.22-1
- Updated to release 2.22

* Fri Feb 05 2021 Dries Verachtert <dries@ulyssis.org> - 2.19-1
- Updated to release 2.19.

* Wed Jun 02 2010 Steve Huff <shuff@vecna.org> - 2.11-1 - 8843/shuff
- Updated to release 2.11.

* Thu May 15 2008 Dries Verachtert <dries@ulyssis.org> - 2.5-1
- Updated to release 2.5.

* Tue Sep 12 2006 Dag Wieers <dag@wieers.com> - 2.1-1
- Updated to release 2.1.

* Sun Mar 19 2006 Dag Wieers <dag@wieers.com> - 2.0-1
- Updated to release 2.0.

* Fri May 20 2005 Dag Wieers <dag@wieers.com> - 1.3-1
- Initial package. (using DAR)
