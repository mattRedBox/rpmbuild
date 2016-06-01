Name: mint-build-distro-initialdata
Version: 1.0
Release: RELEASE
Summary: mint-build-distro-initialdata
License: GPLv2
Group: Application/Internet
autoprov: yes
autoreq: yes
BuildArch: noarch
BuildRoot: /root/rpmbuild/BUILDROOT/%{name}-%{version}.%{buildarch}

%description
unpacks storage and solr initial datafor mint
For rpmbuild, it will include the following python compile and link scripts
#/usr/lib/rpm/brp-python-bytecompile /usr/bin/python
#/usr/lib/rpm/redhat/brp-python-hardlink
These will either need a command at the end to remove these .pyc and .pyo files or the steps are skipped altogether in macro for build/install

%build
if [ ! -z "%{_sourcedir}" ] && [ ! -z "%{_builddir}" ]; then
  cd %{_sourcedir}/storage && tar -cvz * -f %{_builddir}/storage.tar.gz 
  cd %{_sourcedir}/solr && tar -cvz * -f %{_builddir}/solr.tar.gz
else
  echo "no variable for either _sourcedir, %{_sourcedir} or _builddir, %{_builddir}  exists. Exiting"
  exit 1
fi

%install
if [ ! -z "${RPM_BUILD_ROOT}" ] && [ ! -z "%{_builddir}" ]; then
  # ensure that there is no tampering with solr or storage directory itself, as it may be a link
  echo "RPM_BUILD_ROOT is: ${RPM_BUILD_ROOT}"
  %{__install} -d -m0744 "${RPM_BUILD_ROOT}/opt/mint/storage"
  %{__install} -d -m0744 "${RPM_BUILD_ROOT}/opt/mint/solr"

  cp -a %{_builddir}/storage.tar.gz "${RPM_BUILD_ROOT}/opt/mint/storage/"
  cp -a %{_builddir}/solr.tar.gz "${RPM_BUILD_ROOT}/opt/mint/solr/"
else
  echo "no variable for RPMBUILDROOT, ${RPMBUILDROOT} or _builddir, %{_builddir} exists. Exiting"
  exit 1
fi

%files
%defattr(-, redbox, redbox, 0744)
"/opt/mint/storage/storage.tar.gz"
"/opt/mint/solr/solr.tar.gz"

%pre
#!/usr/bin/env bash

if [ `whoami` != 'root' ];
        then echo "this script must be executed as root" && exit 1;
fi

ADMIN_INSTALL_HOME="/opt/mint"

exit_install() {
    if [ $# -gt 0 ]; then
        echo "ERROR: $@." >&2
    fi
    echo "ERROR: rpm pre-install incomplete." >&2
    exit 1
}

log_function() {
 printf  -- "At function: %s...\n" $1
}

stop_server() {
    log_function $FUNCNAME
    ## Added a directory check since in fresh installs, this directory doesn't exist.
    if [ -d ${ADMIN_INSTALL_HOME} ]; then
      service mint stop
      # ensure that there is no tampering with solr or storage directory itself, as it may be a link
      rm -Rf ${ADMIN_INSTALL_HOME}/storage/*
      rm -Rf ${ADMIN_INSTALL_HOME}/solr/indexes/fascinator/index/*
    fi
}

stop_server

%post
#!/usr/bin/env bash

if [ `whoami` != 'root' ];
        then echo "this script must be executed as root" && exit 1;
fi

ADMIN_INSTALL_HOME="/opt/mint"
RB_ADMIN_SERVER_ARGS='start'

exit_install() {
    if [ $# -gt 0 ]; then
        echo "ERROR: $@." >&2
    fi
    echo "ERROR: rpm post-install incomplete." >&2
    exit 1
}

log_function() {
 printf  -- "At function: %s...\n" $1
}

install_server() {
 # ensure that there is no tampering with solr or storage directory itself, as it may be a link
 tar -xvzf ${ADMIN_INSTALL_HOME}/storage/storage.tar.gz -C /opt/mint/storage
 tar -xvzf ${ADMIN_INSTALL_HOME}/solr/solr.tar.gz -C /opt/mint/solr
 chown -R redbox:redbox ${ADMIN_INSTALL_HOME}
 chown -R redbox:redbox ${ADMIN_INSTALL_HOME}/storage/*
 chown -R redbox:redbox ${ADMIN_INSTALL_HOME}/solr/*
 echo 'finished installing'
}
getServerArgs() {
 if ps -efl | pgrep forever > /dev/null; then
  export RB_ADMIN_SERVER_ARGS='restart'
 fi
}

start_server() {
    log_function $FUNCNAME
    cd ${ADMIN_INSTALL_HOME} || exit_install "failed to change to install directory."
    getServerArgs
    service mint restart
}

install_server
start_server
