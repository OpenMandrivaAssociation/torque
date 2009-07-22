%define name    torque
%define version 2.1.11
%define release %mkrel 1
%define lib_name_orig lib%{name}
%define major           1
#define lib_name %mklibname %name %{major}
%define lib_name %mklibname %name%{major}

%define tcl_sitelib_spaced %(echo %tcl_sitelib | sed -e 's,/, ,g')

Name:           %{name}
Summary:        The Portable Batch System
Group:		System/Cluster
Version:        %{version}
Release:        %{release}
License:        OpenPBS
URL:            http://www.clusterresources.com/products/torque-resource-manager.php
Requires:       openssh-clients >= 2.9
Provides:       OpenPBS
BuildRoot:      %{_tmppath}/%{name}-%{version}
Source0:        %{name}-%{version}.tar.gz
Source1:	pbs_server
Source2:	pbs.conf	
Source3:	PBS_doc_v2.3_admin.pdf
Source4:        pbs_mom
Source5:        pbs_sched
Source6:	xpbs
Source7:	xpbsmon
Source8:	tclIndex_xpbsmon
Source9:	tclIndex_xpbs
Source10:	introduction_openPBS
Source11:	xtermPBSlog
Source12:	pbs
Source13:	setup_pbs_server
Source14:	pbs_config.sample
Source15:	pbs_para_job.sh	
Source17:	pbs-epilogue
Source18:	pbs-prologue
Source19:	setup_pbs_client
Patch0:		torque-2.1.11-string-format.patch
Patch9:		torque-2.1.11-pbs_log.patch
Patch13:	torque-2.1.11-destdir.patch
Patch14:	torque-2.1.11-tcl86.patch
BuildRequires:	tk >= 8.3 tk-devel >= 8.3 
BuildRequires:	tcl >= 8.3 tcl-devel >= 8.3
BuildRequires:	openssh openssh-clients
BuildRequires:	X11-devel
Provides:	OpenPBS
Obsoletes:	OpenPBS
Requires(post): rpm-helper
Requires(preun): rpm-helper

%package	-n %{lib_name}-devel
Summary:	The Portable Batch System (PBS) devel 
Group:		Development/Other
Provides:	libOpenPBS0-devel
Obsoletes:	libOpenPBS0-devel
Provides:	lib%name-devel = %version-%release
Provides:	%name-devel = %version-%release

%package	client
Summary:	The Portable Batch System (PBS) client
Requires:       openssh-clients >= 2.9
Group:		System/Cluster
Provides:	OpenPBS-client
Obsoletes:	OpenPBS-client
Requires(post): rpm-helper
Requires(preun): rpm-helper

%package        xpbs
Requires:	tk >= 8.3, tcl >= 8.3, %{name}-client = %{version}-%{release}
Summary:        The Portable Batch System (PBS) X interface 
Group:          Monitoring
Provides:	OpenPBS-xpbs
Obsoletes:	OpenPBS-xpbs

%description
The Portable Batch System (PBS) is a flexible batch software
processing system developed at NASA Ames Research Center. It 
operates on networked, multi-platform UNIX environments, 
including heterogeneous clusters of workstations, supercomputers,
and massively parallel systems.

"This product includes software developed by NASA Ames Research 
Center, Lawrence Livermore National Laboratory, and Veridian 
Information Solutions, Inc. Visit www.OpenPBS.org for OpenPBS 
software support,products, and information."

%description client
The Portable Batch System (PBS) client.
"This product includes software developed by NASA Ames Research 
Center, Lawrence Livermore National Laboratory, and Veridian 
Information Solutions, Inc. Visit www.OpenPBS.org for OpenPBS 
software support,products, and information."

%description -n %{lib_name}-devel
The Portable Batch System (PBS) function prototype.
"This product includes software developed by NASA Ames Research 
Center, Lawrence Livermore National Laboratory, and Veridian 
Information Solutions, Inc. Visit www.OpenPBS.org for OpenPBS 
software support,products, and information."

%description xpbs
The Portable Batch System (PBS) X interface.
"This product includes software developed by NASA Ames Research 
Center, Lawrence Livermore National Laboratory, and Veridian 
Information Solutions, Inc. Visit www.OpenPBS.org for OpenPBS 
software support,products, and information."

%prep
%setup -q -n %name-%version
%patch0 -p1 -b .string_format~
%patch9 -p1 -b .pbs_log~
%patch13 -p1 -b .destdir~
%patch14 -p1 -b .tcl86~

# these variables aren't ever set in any file that gets installed,
# so without doing this, xpbs won't run - AdamW 2008/12
sed -i -e 's,$xpbs_datadump,xpbs_datadump,g' src/gui/pbs.tcl
sed -i -e 's,$xpbs_scriptload,xpbs_scriptload,g' src/gui/pbs.tcl

%ifarch x86_64 ppc64 sparc64
for i in configure.in configure; 
	do 
	perl -pi -e 's|\$\{ac_libpath\}/lib/|\$\{ac_libpath\}/lib64/|g' $i
	perl -pi -e 's|\$\{tcl_dir\}/lib/|\$\{tcl_dir\}/lib64/|g' $i
	perl -pi -e 's|\$TCL_DIR/lib/|\$TCL_DIR/lib64/|g' $i
	perl -pi -e 's|\$TCLX_DIR/lib/|\$TCLX_DIR/lib64/|g' $i
	done
%endif

cp %{SOURCE3} $RPM_BUILD_DIR/%{name}-%{version}/PBS_doc_v2.3_admin.pdf
cp %{SOURCE10} $RPM_BUILD_DIR/%{name}-%{version}/introduction_openPBS
cp %{SOURCE15} $RPM_BUILD_DIR/%{name}-%{version}/para_job_pbs.sh

%pre 
/usr/sbin/groupadd -g 12386 -r -f pbs > /dev/null 2>&1 ||:
# /usr/sbin/useradd -g pbs -d %{pbs_user} -r -s /bin/bash -p "" -m >/dev/null 2>&1 ||:

%pre client
/usr/sbin/groupadd -g 12386 -r -f pbs > /dev/null 2>&1 ||:

%build
%configure2_5x \
	--with-scp \
	--with-server-home=/var/spool/pbs \
	--enable-docs \
	--enable-server \
	--enable-mom \
	--enable-client \
	--srcdir=${RPM_BUILD_DIR}/%{name}-%{version} \
	--enable-gui \
	-x-libraries=%_libdir
	
%ifarch x86_64
	perl -pi -e 's|\-L\$\(TCL\_DIR\)/lib|\-L\$\(TCL\_DIR\)/lib64|g' src/tools/Makefile
%endif 

#make depend
make clean
%make all XPBS_DIR=%{tcl_sitelib}/xpbs XPBSMON_DIR=%{tcl_sitelib}/xpbsmon

%install
rm -rf %{buildroot}
pbs_server_home_for_install=%{buildroot}/var/spool/pbs

mkdir -p %{buildroot}%{_initrddir}
mkdir -p ${pbs_server_home_for_install}/mom_priv/
touch ${pbs_server_home_for_install}/mom_priv/config
mkdir -p ${pbs_server_home_for_install}/sched_priv
chmod 644 ${pbs_server_home_for_install}/mom_priv/config
mkdir -p ${pbs_server_home_for_install}/server_logs
mkdir -p ${pbs_server_home_for_install}/sched_logs
mkdir -p ${pbs_server_home_for_install}/server_priv

mkdir -p %{buildroot}%{_defaultdocdir}
mkdir -p %{buildroot}%{_sysconfdir}
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{tcl_sitelib}/xpbs
mkdir -p %{buildroot}%{tcl_sitelib}/xpbsmon
mkdir -p %{buildroot}%{_libdir}/%{name}-%{version}
mkdir -p %{buildroot}%{_defaultdocdir}/%{name}-%{version}
mkdir -p %{buildroot}%{_defaultdocdir}/%{name}-client-%{version}
mkdir -p %{buildroot}%{_includedir}/%{name}-%{version}

install -m755 %{SOURCE1} %{buildroot}%{_initrddir}/pbs_server
install -m755 %{SOURCE4} %{buildroot}%{_initrddir}/pbs_mom
install -m755 %{SOURCE5} %{buildroot}%{_initrddir}/pbs_sched
install -m755 %{SOURCE12} %{buildroot}%{_initrddir}/openpbs
install -m644 %{SOURCE2} %{buildroot}%{_sysconfdir}/pbs.conf
install -m644 %{SOURCE11} %{buildroot}%{_sbindir}/pbslogs

%makeinstall_std PBS_SERVER_HOME=/var/spool/pbs mandir=%_mandir XPBS_DIR=%{tcl_sitelib}/xpbs XPBSMON_DIR=%{tcl_sitelib}/xpbsmon

mkdir -p %{buildroot}%{_sbindir}
chmod 755 %{buildroot}%{_sbindir}/pbs_mom
chmod 755 %{buildroot}%{_sbindir}/pbs_sched
chmod 755 %{buildroot}%{_sbindir}/pbs_iff
#chmod 755 %{buildroot}%{_sbindir}/pbs_rcp
chmod 755 %{buildroot}%{_sbindir}/pbs_server
chmod 755 %{buildroot}%{_initrddir}/openpbs

# needed to overwrite bad path in those scripts
install -m755 %{SOURCE6} %{buildroot}%{_bindir}/xpbs
install -m755 %{SOURCE7} %{buildroot}%{_bindir}/xpbsmon
install -m755 %{SOURCE13} %{buildroot}%{_bindir}/setup_pbs_server
install -m755 %{SOURCE19} %{buildroot}%{_bindir}/setup_pbs_client
install -m644 %{SOURCE8} %{buildroot}%{tcl_sitelib}/xpbsmon/tclIndex
install -m644 %{SOURCE9} %{buildroot}%{tcl_sitelib}/xpbs/tclIndex
install -m644 %{SOURCE14} %{buildroot}%{_var}/spool/pbs/pbs_config.sample
install -m755 %{SOURCE17} %{buildroot}%{_var}/spool/pbs/mom_priv/epilogue
install -m755 %{SOURCE18} %{buildroot}%{_var}/spool/pbs/mom_priv/prologue

# replace the placeholder text with whatever the real tcl_sitelib
# should be...cunning, eh? - AdamW 2008/12
sed -i -e 's,TCL_SITELIB,%{tcl_sitelib},g' \
%{buildroot}%{tcl_sitelib}/xpbsmon/tclIndex \
%{buildroot}%{tcl_sitelib}/xpbs/tclIndex \
%{buildroot}%{_bindir}/xpbs \
%{buildroot}%{_bindir}/xpbsmon \
%{buildroot}%{_bindir}/setup_pbs_server \
%{buildroot}%{_bindir}/setup_pbs_client

rm -f %{buildroot}%{_libdir}/xpbs/tclIndex
rm -f %{buildroot}%{_libdir}/xpbsmon/tclIndex

echo "# MOM server configuration file" > ${pbs_server_home_for_install}/mom_priv/config
echo "# if more than one value, separate it by comma." >> ${pbs_server_home_for_install}/mom_priv/config

cp -av $RPM_BUILD_DIR/%{name}-%{version}/src/include/* %{buildroot}%{_includedir}/%{name}-%{version}/

perl -pi -e 's/wish8\.3/wish/' %buildroot%_bindir/xpbs

%multiarch_includes $RPM_BUILD_ROOT%{_includedir}/%{name}-%{version}/pbs_config.h

%clean
rm -rf ${RPM_BUILD_ROOT}

%post
#!/bin/sh
pbs_prefix=%_prefix
pbs_server_home=/var/spool/pbs
if [ -f "${pbs_server_home}/server_name" ]; then
        echo `hostname` > ${pbs_server_home}/server_name
fi
#if [ ! -f "${pbs_server_home}/default_server" ] ; then
#        echo "# <server hostname>" > ${pbs_server_home}/default_server
#fi
if [ -f "${pbs_server_home}/default_server" ]; then
        echo `hostname` >> ${pbs_server_home}/default_server
fi
if [ ! -f "${pbs_server_home}/server_priv/nodes" ]; then
	echo `hostname` > ${pbs_server_home}/server_priv/nodes
fi

# add pbs service
%_post_service pbs_server
# %_post_service pbs_sched

# mise a jour /etc/services if needed
CHECK_PORT=`grep 15003 /etc/services`
if [ -z "$CHECK_PORT" ]; then
	cat >> /etc/services << EOF
# Port needed by PBS
pbs_server	15001/tcp	# pbs server
pbs_mom		15002/tcp	# mom to/from server
pbs_resmon	15003/tcp   # mom resource management requests
pbs_resmon      15003/udp   # mom resource management requests
pbs_sched	15004/tcp   # scheduler 
EOF
fi
	
%post client
%_post_service pbs_mom

%post xpbs
ln -sf %{tcl_sitelib}/xpbs /usr/lib/xpbs
ln -sf %{tcl_sitelib}/xpbsmon /usr/lib/xpbsmon

%preun
%_preun_service pbs_server

%preun client
%_preun_service pbs_mom

%if %mdkversion < 200900
%postun -p /sbin/ldconfig
%endif

%files
%defattr(-,root,root)
%doc doc/READ_ME PBS_License.txt 
%attr(755,root,root) %{_initrddir}/pbs_server
%attr(755,root,root) %{_initrddir}/pbs_sched
%attr(755,root,root) %{_initrddir}/openpbs
%attr(644,root,root) %{_mandir}/man1/pbs*
%attr(644,root,root) %{_mandir}/man3/pbs*
%attr(644,root,root) %{_mandir}/man7/*
%attr(644,root,root) %{_mandir}/man8/pbsnodes*
%attr(644,root,root) %{_mandir}/man8/pbs_server.8*
%attr(644,root,root) %{_mandir}/man8/pbs_sch*
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/pbs.conf
%attr(755,root,root) %{_sbindir}/pbs_server
%attr(755,root,root) %{_sbindir}/pbs_sched
%attr(755,root,root) %{_sbindir}/pbslogs
%attr(755,root,root) %{_bindir}/pbsnodes
%attr(755,root,root) %{_bindir}/setup_pbs_server
%attr(755,root,root) %{_bindir}/pbs-config
%attr(755,root,root) %{_bindir}/printtracking
%attr(755,root,root) %{_var}/spool/pbs/sched_logs/
%dir %{_var}/spool/pbs
%{_var}/spool/pbs/sched_priv
%attr(755,root,root) %{_var}/spool/pbs/server_logs/
%attr(755,root,root) %{_var}/spool/pbs/checkpoint/
%attr(755,root,root) %{_var}/spool/pbs/server_priv/
%attr(775,root,pbs) %{_var}/spool/pbs/spool/
%attr(1777,root,pbs) %{_var}/spool/pbs/undelivered/
%attr(644,root,root) %config(noreplace) %{_var}/spool/pbs/pbs_environment
%attr(644,root,root) %config(noreplace) %{_var}/spool/pbs/server_name
%attr(644,root,root) %{_var}/spool/pbs/pbs_config.sample

%files client
%defattr(-,root,root)
%doc PBS_doc_v2.3_admin.pdf introduction_openPBS para_job_pbs.sh PBS_License.txt
%attr(755,root,root) %{_sbindir}/momctl
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/pbs.conf
%attr(755,root,root) %{_var}/spool/pbs/aux
%attr(644,root,root) %{_mandir}/man1/q*
%attr(644,root,root) %{_mandir}/man8/q*
%attr(644,root,root) %{_mandir}/man8/pbsnodes*
%attr(644,root,root) %{_mandir}/man8/pbs_mom.8*
%attr(644,root,root) %{_mandir}/man1/bas*
%attr(644,root,root) %{_mandir}/man1/nqs*
%dir %{_var}/spool/pbs
%{_var}/spool/pbs/mom_logs
%{_var}/spool/pbs/mom_priv
%attr(755,root,root) %{_var}/spool/pbs/checkpoint
%attr(1777,root,pbs) %{_var}/spool/pbs/undelivered
%attr(775,root,pbs) %{_var}/spool/pbs/spool
%attr(644,root,root) %config(noreplace) %{_var}/spool/pbs/pbs_environment
%attr(755,root,root) %{_bindir}/q*
%attr(755,root,root) %{_bindir}/chk_tree
%attr(755,root,root) %{_bindir}/hostn
%attr(755,root,root) %{_bindir}/nqs2pbs
%attr(755,root,root) %{_bindir}/printjob
%attr(755,root,root) %{_bindir}/tracejob
%attr(755,root,root) %{_bindir}/pbsnodes
%attr(755,root,root) %{_bindir}/pbsdsh
%attr(755,root,root) %{_bindir}/setup_pbs_client
%attr(755,root,root) %{_sbindir}/pbs_demux
%attr(4755,root,root) %{_sbindir}/pbs_iff
%attr(755,root,root) %{_sbindir}/pbs_mom
%attr(755,root,root) %{_initrddir}/pbs_mom
%attr(644,root,root) %config(noreplace) %{_var}/spool/pbs/server_name

%files -n %{lib_name}-devel
%defattr(-,root,root)
%doc PBS_License.txt
%{_libdir}/*.la
%{_libdir}/*.so*
%{_libdir}/*.a
%attr(644,root,root) %{_mandir}/man3/tm*
%attr(644,root,root) %{_mandir}/man3/rpp.3.*
%attr(755,root,root) %{_includedir}/%{name}-%{version}
%attr(644,root,root) %{_includedir}/*.h
%multiarch %{multiarch_includedir}/%{name}-%{version}/pbs_config.h

%files xpbs
%defattr(-,root,root)
%doc PBS_License.txt
%attr(755,root,root) %{_bindir}/pbs_tclsh
%attr(755,root,root) %{_bindir}/pbs_wish
%attr(755,root,root) %{_bindir}/xpbsmon
%attr(755,root,root) %{_bindir}/xpbs
%dir %{tcl_sitelib}/xpbs/bitmaps
%attr(644,root,root) %{tcl_sitelib}/xpbs/bitmaps/*
%dir %{tcl_sitelib}/xpbs/help
%attr(644,root,root) %{tcl_sitelib}/xpbs/help/*
%dir %{tcl_sitelib}/xpbs/bin
%attr(755,root,root) %{tcl_sitelib}/xpbs/bin/*
%attr(644,root,root) %{tcl_sitelib}/xpbs/preferences.tcl
%attr(644,root,root) %{tcl_sitelib}/xpbs/pbs.tcl
%attr(644,root,root) %{tcl_sitelib}/xpbs/*.tk
%attr(644,root,root) %{tcl_sitelib}/xpbs/tclIndex
%attr(644,root,root) %config(noreplace) %{tcl_sitelib}/xpbs/xpbsrc
%attr(644,root,root) %{tcl_sitelib}/xpbs/buildindex
%attr(644,root,root) %{tcl_sitelib}/xpbsmon/buildindex
%attr(644,root,root) %{tcl_sitelib}/xpbsmon/*.tk
%attr(644,root,root) %{tcl_sitelib}/xpbsmon/*.tcl
%attr(644,root,root) %{tcl_sitelib}/xpbsmon/tclIndex
%attr(644,root,root) %config(noreplace) %{tcl_sitelib}/xpbsmon/xpbsmonrc
%dir %{tcl_sitelib}/xpbsmon
%dir %{tcl_sitelib}/xpbsmon/bitmaps
%attr(644,root,root) %{tcl_sitelib}/xpbsmon/bitmaps/*
%attr(644,root,root) %{tcl_sitelib}/xpbsmon/help/*
%attr(644,root,root) %{_mandir}/man1/x*


