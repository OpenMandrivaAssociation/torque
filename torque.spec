%define _disable_ld_no_undefined   1

%define major 2
%define libname %mklibname %{name} %{major}
%define devname %mklibname -d %{name}

%define clientname %{name}-client
%define servername %{name}-server
%define schedname %{name}-sched
%define momname %{name}-mom
%define guiname %{name}-gui

#default is /var/spool/torque: if you change this, you'll break some
#scripts coming along with the source files
%define torquedir /var/spool/torque
%define srcversion %{version}
%bcond_with gui

Summary:	The Torque resource and queue manager
Name:		torque
Group:		System/Cluster
Version:	6.1.3.h5
Release:	4
License:	TORQUEv1.1
URL:		https://www.adaptivecomputing.com/products/open-source/torque/
Source0:	https://github.com/adaptivecomputing/torque/archive/refs/heads/%{version}.tar.gz
Source1:	mom_config
Source2:	README.omv
Source7:	torque_addport
Source8:	torque_createdb
Source9:	openmp.pbs
Patch0:		torque-6.1.3-skip-broken-pthreads-check.patch
Patch1:		torque-6.1.3-compile.patch
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	groff
BuildRequires:	groff-for-man
BuildRequires:	xauth
BuildRequires:	gperf
BuildRequires:	doxygen
BuildRequires:	pkgconfig(ncurses)
%if %{with gui}
BuildRequires:	pkgconfig(tk)
%endif
BuildRequires:	pkgconfig(tcl)
BuildRequires:	openssh-clients
BuildRequires:	readline-devel
BuildRequires:	gcc-gfortran
BuildRequires:	gcc-c++
%ifarch %ix86 %{x86_64}
BuildRequires:	quadmath-devel
%endif
BuildRequires:	pam-devel
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(hwloc)
BuildRequires:	boost-devel
BuildRequires:	glibc-static-devel
BuildRequires:	glibc-devel
BuildRequires:	pkgconfig(libsystemd)
# Just so configure knows we're using it
BuildRequires:	systemd

Requires:	openssh-clients
Recommends:	torque-mom

%description
The Tera-scale Open-source Resource and QUEue manager provides control
over batch jobs and distributed computing resources. It is an advanced
open-source product based on the original PBS project* and
incorporates the best of both community and professional
development. It incorporates significant advances in the areas of
scalability, reliability, and functionality and is currently in use at
tens of thousands of leading government, academic, and commercial
sites throughout the world. Please check out the README.mga file provided in
%{_docdir}/%{name} for setting up a minimal running system.

"TORQUE is a modification of OpenPBS which was developed by NASA Ames
Research Center, Lawrence Livermore National Laboratory, and Veridian
Information Solutions, Inc. Visit www.clusterresources.com/products/
for more information about TORQUE and to download TORQUE".

%package -n %{libname}
Summary:	Shared libraries for Torque
Group:		System/Libraries
Provides:	lib%{name} = %{version}-%{release}

%description -n %{libname}
%{summary}.

%package -n %{devname}
Summary:	Development files for Torque
Group:		Development/Other
Requires:	%{libname} = %{version}-%{release}
Provides:	lib%{name}-devel  = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{devname}
%{summary}.

%package -n %{clientname}
Summary:	Command line utilities for Torque
Group:		System/Cluster
Requires:	%{libname} = %{version}-%{release}
Requires:	%{name} = %{version}-%{release}

%description -n %{clientname}
%{summary}.

%package -n     %{servername}
Summary:	The Torque server
Group:		System/Cluster
Requires:	%{libname} = %{version}-%{release}
Requires:	%{name} = %{version}-%{release}
Recommends:	%{schedname} = %{version}-%{release}
Requires(post):	rpm-helper
Requires(preun):	rpm-helper

%description -n %{servername}
%{summary}.

%package -n     %{schedname}
Summary:	The scheduler for Torque server
Group:		System/Cluster
Requires:	%{libname} = %{version}-%{release}
Requires:	%{name} = %{version}-%{release}
Requires:	%{servername} = %{version}-%{release}
Requires(post):	rpm-helper
Requires(preun):	rpm-helper

%description -n %{schedname}
%{summary}.

%package -n %{momname}
Summary:	Node manager programs for Torque
Group:		System/Cluster
Requires:	%{libname} = %{version}-%{release}
Requires:	%{name} = %{version}-%{release}
Requires:	openssh-server
Requires(post):	rpm-helper
Requires(preun):	rpm-helper

%description -n %{momname}
%{summary}.

%package -n %{guiname}
Summary:	Graphical clients for Torque
Group:		Monitoring
Requires:	tk
Requires:	tcl
Requires:	%{libname} = %{version}-%{release}
Requires:	%{name} = %{version}-%{release}
Requires:	%{name}-client = %{version}-%{release}
Obsoletes:	torque-xpbs <= 2.5.3

%description -n %{guiname}
%{summary}.

%prep
%autosetup -p1 -n %{name}-%{srcversion}
# fix checks for systemd in Makefile.am files that
# don't work inside containerized builders
find . -name Makefile.am |xargs sed -i -e 's,if systemctl.*,if true; then \\,'

%build
autoreconf -fi
# -fpermissive added to downgrade numerous 'invalid conversion' errors to warnings
export CPPFLAGS="-DUSE_INTERP_RESULT -DUSE_INTERP_ERRORLINE -DHAVE_STDBOOL_H -fpermissive"
%configure \
	--srcdir=%{_builddir}/%{name}-%{srcversion} \
	--includedir=%{_includedir}/%{name} \
	--with-pam=%{_libdir}/security \
	--with-rcp=scp \
	--with-hwloc-path=%{_prefix} \
	--enable-docs \
	--enable-server \
	--enable-mom \
	--enable-client \
	--enable-drmaa \
	--enable-high-availability \
	--enable-syslog \
	--disable-static \
	--with-default-server=MYSERVERNAME \
	--enable-autorun \
	--enable-cpuset \
	--without-debug
#                --enable-nvidia-gpus
#                --enable-numa-support

%make_build all \
	XPBS_DIR=%{tcl_sitelib}/xpbs \
	XPBSMON_DIR=%{tcl_sitelib}/xpbsmon

%install
%make_install \
	PBS_SERVER_HOME=%{torquedir} \
	mandir=%{_mandir} \
	XPBS_DIR=%{tcl_sitelib}/xpbs \
	XPBSMON_DIR=%{tcl_sitelib}/xpbsmon


find %{buildroot}%{_libdir} -name *.la -delete

#yields various service to fail if relative symlinks
export DONT_RELINK=1

install -p -m 644 contrib/systemd/pbs_sched.service %{buildroot}%{_unitdir}/

rm -f %{buildroot}%{_sysconfdir}/init.d/pbs_mom
rm -f %{buildroot}%{_sysconfdir}/init.d/pbs_server
rm -f %{buildroot}%{_sysconfdir}/init.d/trqauthd

#end starting scripts

#install configuration scripts
install -p -m 755 %{SOURCE7} %{buildroot}%{_sbindir}/torque_addport
install -p -m 755 %{SOURCE8} %{buildroot}%{_sbindir}/torque_createdb
#end configuration scripts

#install config files: move them to /etc/torque
%__mkdir_p %{buildroot}%{_sysconfdir}/%{name}
pushd %{buildroot}%{torquedir}
%__mv server_name     %{buildroot}%{_sysconfdir}/%{name}
%__ln_s               %{_sysconfdir}/%{name}/server_name .
popd

pushd %{buildroot}%{torquedir}/server_priv
%__mv nodes %{buildroot}%{_sysconfdir}/%{name}
%__ln_s     %{_sysconfdir}/%{name}/nodes .
popd

pushd %{buildroot}%{torquedir}/sched_priv
%__mv sched_config   %{buildroot}%{_sysconfdir}/%{name}
%__mv dedicated_time %{buildroot}%{_sysconfdir}/%{name}
%__mv holidays       %{buildroot}%{_sysconfdir}/%{name}
%__mv resource_group %{buildroot}%{_sysconfdir}/%{name}
%__ln_s               %{_sysconfdir}/%{name}/sched_config .
%__ln_s               %{_sysconfdir}/%{name}/dedicated_time .
%__ln_s               %{_sysconfdir}/%{name}/holidays .
%__ln_s               %{_sysconfdir}/%{name}/resource_group .
popd

install -p -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}
pushd %{buildroot}%{torquedir}/mom_priv
%__ln_s %{_sysconfdir}/%{name}/mom_config config

popd
#end config files

#move drmaa man to the right place and install docs
##__mv #{buildroot}#{_defaultdocdir}/torque-drmaa/man/man3/* #{buildroot}#{_mandir}/man3/.
install -D -m 644 %{SOURCE2} %{buildroot}%{_docdir}/%{name}/README.mga
install -D -m 644 %{SOURCE9} %{buildroot}%{_docdir}/%{name}/openmp.pbs

%if %{with gui}
#make symbolic links for tcl
pushd %{buildroot}%{_libdir}
%__ln_s %{tcl_sitelib}/xpbs    .
%__ln_s %{tcl_sitelib}/xpbsmon .
popd
%endif

#clean make install bugs the dirty way...
%__rm -f %{buildroot}%{_mandir}/man1/basl2c.1*
#__rm -f #{buildroot}#{_mandir}/man3/_*src_drmaa_src_.3*

%post
#update of /etc/services if needed
%{_sbindir}/torque_addport
sed -i 's|MYSERVERNAME|'"$HOSTNAME"'|g' %{_sysconfdir}/%{name}/server_name

%post -n %{momname}
%_post_service pbs_mom
sed -i 's|MYSERVERNAME|'"$HOSTNAME"'|g' %{_sysconfdir}/%{name}/mom_config

%preun -n %{momname}
%_preun_service pbs_mom

%post -n %{servername}
#create serverdb if needed
%{_sbindir}/torque_createdb %{torquedir} %{_sbindir}/pbs_server
sed -i 's|MYSERVERNAME|'"$HOSTNAME"'|g' %{torquedir}/server_priv/serverdb
%_post_service pbs_server

%preun -n %{servername}
%_preun_service pbs_server

%post -n %{schedname}
%_post_service pbs_sched

%preun -n %{schedname}
%_preun_service pbs_sched

%post -n %{clientname}
%_post_service trqauthd

%preun -n %{clientname}
%_preun_service trqauthd

%files
%doc PBS_License.txt Release_Notes README.torque
%doc README.NUMA README.trqauthd README.array_changes
%{_docdir}/%{name}/README.mga
%{_docdir}/%{name}/openmp.pbs
%dir %{torquedir}
%dir %{torquedir}/checkpoint
%dir %{torquedir}/aux
%dir %{torquedir}/spool
%dir %{torquedir}/undelivered
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/server_name
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/torque.conf
%config(noreplace) %{_sysconfdir}/profile.d/torque.*
%{_sbindir}/torque_addport
%{torquedir}/server_name
%{torquedir}/pbs_environment
%{_libdir}/security/pam*
%doc %{_mandir}/man1/pbs.1.*

%files -n %{libname}
%doc CHANGELOG README.coding_notes README.building_40 README.configure
%{_libdir}/*.so.*

%files -n %{devname}
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*
%{_bindir}/pbs-config
%{_libdir}/*.so
%{_defaultdocdir}/torque-drmaa
%doc %{_mandir}/man3/pbs_*.3*
#{_mandir}/man3/rpp.3*
%doc %{_mandir}/man3/tm.3*
#{_mandir}/man3/drmaa.3*
#{_mandir}/man3/drmaa_*.3*

%files -n %{clientname}
%doc
%{_unitdir}/trqauthd.service
%{_sbindir}/trqauthd
%{_bindir}/qa*
%{_bindir}/qc*
%{_bindir}/qdel
%{_bindir}/qg*
%{_bindir}/qh*
%{_bindir}/qm*
%{_bindir}/qo*
%{_bindir}/qrerun
%{_bindir}/qrls
%{_bindir}/qsub
%{_bindir}/qstat
%{_bindir}/qsig
%{_bindir}/qselect
%{_bindir}/chk_tree
%{_bindir}/hostn
%{_bindir}/nqs2pbs
%{_bindir}/pbsnodes
%{_bindir}/qnodes
%{_bindir}/pbsdsh
%{_bindir}/qterm
%{_bindir}/qstop
%{_bindir}/qstart
%{_bindir}/qdisable
%{_bindir}/qenable
%{_bindir}/qrun
%doc %{_mandir}/man1/q*.1*
%doc %{_mandir}/man1/nqs2pbs.1*
%doc %{_mandir}/man1/pbsdsh.1*
#{_mandir}/man3/jobs.3*
%doc %{_mandir}/man7/pbs_*.7*
%doc %{_mandir}/man8/pbsnodes.8*
%doc %{_mandir}/man8/q*.8*

%files -n %{servername}
%dir %{torquedir}/server_priv
%dir %{torquedir}/server_priv/acl_svr
%dir %{torquedir}/server_priv/acl_groups
%dir %{torquedir}/server_priv/acl_hosts
%dir %{torquedir}/server_priv/acl_users
%dir %{torquedir}/server_priv/accounting
%dir %{torquedir}/server_priv/arrays
%dir %{torquedir}/server_priv/credentials
%dir %{torquedir}/server_priv/disallowed_types
%dir %{torquedir}/server_priv/hostlist
%dir %{torquedir}/server_priv/jobs
%dir %{torquedir}/server_priv/queues
%config(noreplace) %{_sysconfdir}/%{name}/nodes
%{torquedir}/server_priv/nodes
%{_unitdir}/pbs_server.service
%{_sbindir}/torque_createdb
%{_sbindir}/pbs_server
%{_sbindir}/qserverd
%{_bindir}/pbs_track
%{_bindir}/tracejob
%{_bindir}/printjob
%{_bindir}/printserverdb
%{_bindir}/printtracking
%doc %{_mandir}/man8/pbs_server.8*

%files -n %{schedname}
%dir %{torquedir}/sched_priv
%dir %{torquedir}/sched_priv/accounting
%dir %{torquedir}/sched_logs
%config(noreplace) %{_sysconfdir}/%{name}/sched_config 
%config(noreplace) %{_sysconfdir}/%{name}/dedicated_time 
%config(noreplace) %{_sysconfdir}/%{name}/holidays 
%config(noreplace) %{_sysconfdir}/%{name}/resource_group
%{torquedir}/sched_priv/sched_config
%{torquedir}/sched_priv/dedicated_time
%{torquedir}/sched_priv/holidays
%{torquedir}/sched_priv/resource_group
%{_unitdir}/pbs_sched.service
%{_sbindir}/pbs_sched
%{_sbindir}/qschedd
%doc %{_mandir}/man8/pbs_sched*.8*

%files -n %{momname}
%dir %{torquedir}/mom_priv
%dir %{torquedir}/mom_priv/jobs
%dir %{torquedir}/mom_logs
%config(noreplace) %{_sysconfdir}/%{name}/mom_config
%{torquedir}/mom_priv/config
%{_unitdir}/pbs_mom.service
%{_sbindir}/pbs_mom
%{_sbindir}/qnoded
%{_sbindir}/momctl
%{_sbindir}/pbs_demux
%doc %{_mandir}/man8/pbs_mom.8*

%files -n %{guiname}
%{_bindir}/pbs_tclsh
%if %{with gui}
%{_bindir}/xpbs*
%{_bindir}/pbs_wish
%{tcl_sitelib}/xpbs
%{tcl_sitelib}/xpbsmon
%{_libdir}/xpbs
%{_libdir}/xpbsmon
%endif
%doc %{_mandir}/man1/xpbs*.1*
