Name:             rspamd
Version:          3.12.1
Release:	  1%{?dist}
Summary:          Rapid spam filtering system
Group:            System Environment/Daemons
License:          Apache-2.0
URL:              https://rspamd.com
Source0:          https://github.com/rspamd/rspamd/archive/%{version}/%{name}-%{version}.tar.gz
Source1:          %{name}.logrotate
Source2:          80-rspamd.preset
Patch0:           rspamd-3.12-openssl35-build.patch

BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}
%if 0%{?rhel} == 6
BuildRequires:    cmake3
BuildRequires:    devtoolset-9-gcc-c++
BuildRequires:    scl-libarchive-libarchive-devel
%endif
%if 0%{?rhel} == 7
BuildRequires:    cmake3
BuildRequires:    devtoolset-10-gcc-c++
BuildRequires:    scl-libarchive-libarchive-devel
%endif
%if 0%{?rhel} <= 7
BuildRequires:    pkgconfig(openssl11)
%endif
%if 0%{?rhel} == 8
BuildRequires:    gcc-toolset-11-gcc-c++
BuildRequires:    gcc-toolset-11-annobin
BuildRequires:    gcc-annobin-11-build
BuildRequires:    cmake
BuildRequires:    libarchive-devel
BuildRequires:    openssl-devel
%endif
%if 0%{?rhel} >= 8
BuildRequires:    cmake
%endif
%if 0%{?rhel} >= 9
BuildRequires:    gcc-c++
BuildRequires:    libarchive-devel
BuildRequires:    openssl-devel
%endif
BuildRequires:    file-devel
BuildRequires:    glib2-devel
BuildRequires:    hyperscan-devel
BuildRequires:    jemalloc-devel
BuildRequires:    lapack-devel
BuildRequires:    libevent-devel
BuildRequires:    libicu-devel
BuildRequires:    libsodium-devel
BuildRequires:    libunwind-devel
BuildRequires:    luajit-devel
BuildRequires:    openblas-devel
BuildRequires:    pcre2-devel
BuildRequires:    ragel
BuildRequires:    sqlite-devel
Requires(pre):    shadow-utils
%if 0%{?rhel} > 6
BuildRequires:    systemd
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
%endif

%description
Rspamd is a rapid, modular and lightweight spam filter. It is designed to work
with big amount of mail and can be easily extended with own filters written in
lua.

%prep
%setup -q
%patch -p0 -P1 -b .openssl35-build


%build
%if 0%{?rhel} == 8
source /opt/rh/gcc-toolset-11/enable
%endif
%if 0%{?rhel} == 7
source /opt/rh/devtoolset-10/enable

%define libarchive_prefix /opt/ddnet/scl-libarchive/root/usr

#export LDFLAGS+=" -L%{libarchive_prefix}/%{_lib}"
#export LDFLAGS+=" -Wl,-rpath=%{libarchive_prefix}/%{_lib}"
OLD_PKG_CONFIG_PATH=$PKG_CONFIG_PATH
export PKG_CONFIG_PATH="%{libarchive_prefix}/%{_lib}/pkgconfig:$OLD_PKG_CONFIG_PATH"
#export CPPFLAGS="$CPPFLAGS $(pkg-config --cflags-only-I libarchive)"
%endif

%if 0%{?rhel} == 6
source /opt/rh/devtoolset-9/enable
#source /opt/rh/gcc-toolset-9/enable
%endif

%if 0%{?rhel} <= 7
export CFLAGS="$CFLAGS $(pkg-config --cflags openssl11)"
export LDFLAGS="$LDFLAGS $(pkg-config --libs openssl11)"
##OLD_PKG_CONFIG_PATH=$PKG_CONFIG_PATH
##export PKG_CONFIG_PATH="%{_includedir}/openssl11:$OLD_PKG_CONFIG_PATH"
#export OPENSSL_ROOT_DIR=/usr/include/openssl11
#export OPENSSL_INCLUDE_DIR=/usr/include/openssl11
#export OPENSSL_LIBRARIES_DIR=/usr/lib64/openssl11
#export OPENSSL_LIBRARIES=/usr/lib64/openssl11
%endif


%if 0%{?rhel} <= 7
%{__cmake3} \
%else
%{__cmake} \
%endif
        -DCMAKE_BUILD_TYPE="Release" \
        -DCMAKE_C_FLAGS_RELEASE="%{optflags}" \
        -DCMAKE_CXX_FLAGS_RELEASE="%{optflags}" \
%if 0%{?rhel} <= 7
        -DOPENSSL_ROOT_DIR=/usr/include/openssl11 \
	-DOPENSSL_INCLUDE_DIR=/usr/include/openssl11 \
	-DOPENSSL_LIBRARIES=/usr/lib64/openssl11 \
%endif
%if 0%{?rhel} > 9
        -DOPENSSL_ROOT_DIR=/usr/include/openssl \
        -DOPENSSL_INCLUDE_DIR=/usr/include/openssl \
        -DOPENSSL_LIBRARIES=/usr/lib64/openssl \
%endif
%if 0%{?fedora} >= 36
        -DLINKER_NAME=/usr/bin/ld.bfd \
%endif
        -DCMAKE_INSTALL_PREFIX=%{_prefix} \
        -DCONFDIR=%{_sysconfdir}/rspamd \
        -DMANDIR=%{_mandir} \
        -DDBDIR=%{_localstatedir}/lib/rspamd \
        -DRUNDIR=%{_localstatedir}/run/rspamd \
        -DLOGDIR=%{_localstatedir}/log/rspamd \
        -DEXAMPLESDIR=%{_datadir}/examples/rspamd \
        -DSHAREDIR=%{_datadir}/rspamd \
        -DLIBDIR=%{_libdir}/rspamd/ \
        -DINCLUDEDIR=%{_includedir} \
        -DRSPAMD_GROUP=_rspamd \
        -DRSPAMD_USER=_rspamd \
        -DSYSTEMDDIR=%{_unitdir} \
%if 0%{?rhel} > 6
        -DWANT_SYSTEMD_UNITS=ON \
%else
        -DWANT_SYSTEMD_UNITS=OFF \
%endif
        -DNO_SHARED=ON \
	-DNO_TARGET_VERSIONS=1 \
	-DENABLE_LIBUNWIND=ON \
        -DENABLE_HYPERSCAN=ON \
        -DENABLE_JEMALLOC=ON \
        -DENABLE_LUAJIT=ON \
        -DENABLE_BLAS=ON

%{__make} %{?jobs:-j%jobs}

%install
%{__make} install DESTDIR=%{buildroot} INSTALLDIRS=vendor
%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_presetdir}/80-rspamd.preset
%{__install} -d -p -m 0755 %{buildroot}%{_localstatedir}/log/rspamd
%{__install} -d -p -m 0755 %{buildroot}%{_localstatedir}/lib/rspamd
%{__install} -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/local.d/
%{__install} -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/override.d/

%clean
rm -rf %{buildroot}

%pre
%{_sbindir}/groupadd -r _rspamd 2>/dev/null || :
%{_sbindir}/useradd -g _rspamd -c "Rspamd user" -s /bin/false -r -d %{_localstatedir}/lib/rspamd _rspamd 2>/dev/null || :

%post
%{__chown} -R _rspamd:_rspamd %{_localstatedir}/lib/rspamd
%{__chown} _rspamd:_rspamd %{_localstatedir}/log/rspamd
systemctl --no-reload preset %{name}.service >/dev/null 2>&1 || :

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%defattr(-,root,root,-)

%dir %{_sysconfdir}/rspamd
%config(noreplace) %{_sysconfdir}/rspamd/*

%{_bindir}/rspamd
%{_bindir}/rspamd_stats
%{_bindir}/rspamc
%{_bindir}/rspamadm

%{_unitdir}/%{name}.service
%{_presetdir}/80-rspamd.preset

%dir %{_libdir}/rspamd
%{_libdir}/rspamd/*

%{_mandir}/man8/%{name}.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man1/rspamadm.*

%dir %{_datadir}/rspamd
%{_datadir}/rspamd/*

%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%attr(-, _rspamd, _rspamd) %dir %{_localstatedir}/lib/rspamd
%dir %{_localstatedir}/log/rspamd

%changelog
* Tue Jun 17 2025 Michael Seevogel <michael@michaelseevogel.de> - 3.12.1-1
- Update to 3.12.1

* Mon Jun 09 2025 Michael Seevogel <michael@michaelseevogel.de> - 3.12.0-1
- Update to 3.12.0

