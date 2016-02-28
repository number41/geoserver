# Don't repack jars
%define __jar_repack %{nil}

# Don't grok for OSGI dependencies
%define __osgi_provides %{nil}
%define __osgi_requires %{nil}

Name:       geoserver
Version:    2.8.2
Release:    1%{?dist}
Summary:    Open source server for sharing geospatial data

Group:      Applications/Internet    
License:    GPL    
URL:        http://geoserver.org    
Source0:    http://downloads.sourceforge.net/%{name}/%{name}-%{version}-bin.zip
Source1:    %{name}.sysconfig
Source2:    %{name}.service

Requires(pre):      /usr/sbin/useradd
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd
BuildRequires:      systemd

BuildArch:          noarch

%description
GeoServer is an open source software server written in Java that allows users
to share and edit geospatial data. Designed for interoperability, it publishes
data from any major spatial data source using open standards.

%prep
%{__unzip} %{SOURCE0}

%build


%install
# More things go in /usr/share/geoserver than don't, so just copy everything
# over and replace those that don't belong with links to the real things
%{__mkdir_p} %{buildroot}%{_datarootdir}/%{name}
%{__cp} -r %{name}-%{version}/* %{buildroot}%{_datarootdir}/%{name}
%{__rm} -rf %{buildroot}%{_datarootdir}/%{name}/etc
%{__rm} -rf %{buildroot}%{_datarootdir}/%{name}/logs
%{__rm} -rf %{buildroot}%{_datarootdir}/%{name}/data_dir

# Configs go in the standard place
%{__mkdir_p} %{buildroot}%{_sysconfdir}/%{name}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig
%{__mkdir_p} %{buildroot}%{_unitdir}

%{__cp} %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__cp} %{SOURCE2} %{buildroot}%{_unitdir}
%{__cp} %{name}-%{version}/etc/* %{buildroot}%{_sysconfdir}/%{name}
%{__ln_s} %{_sysconfdir}/%{name} %{buildroot}%{_datarootdir}/%{name}/etc

# Logs also go in the standard place
%{__mkdir_p} %{buildroot}%{_localstatedir}/log/%{name}
%{__ln_s} %{_localstatedir}/log/%{name} %{buildroot}%{_datarootdir}/%{name}/logs

# The best practice for the data_dir from RPM is still a work in progress.
# For now, have the default data_dir in /var/lib, and let the admin override
# it from /etc/sysconfig
%{__mkdir_p} %{buildroot}%{_localstatedir}/lib/%{name}
%{__cp} -r %{name}-%{version}/data_dir/* %{buildroot}%{_localstatedir}/lib/%{name}
%{__ln_s} %{_localstatedir}/lib/%{name} %{buildroot}%{_datarootdir}/%{name}/data_dir


%pre
/usr/sbin/useradd -c 'geoserver' -s /sbin/nologin -r \
    -d %{_datarootdir}/%{name} geoserver 2> /dev/null || :

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/%{name}/*
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}

%attr(0755,geoserver,geoserver) %dir %{_localstatedir}/log/%{name}

%attr(0755,geoserver,geoserver) %{_datarootdir}/%{name}/bin/*
%defattr(-,geoserver,geoserver)
%{_datarootdir}/%{name}/etc
%{_datarootdir}/%{name}/data_dir
%doc %{_datarootdir}/%{name}/*txt
%{_datarootdir}/%{name}/lib
%{_datarootdir}/%{name}/logs
%{_datarootdir}/%{name}/resources
%{_datarootdir}/%{name}/start.jar
%{_datarootdir}/%{name}/webapps

# GeoServer stores most of it's programmatic config in the data_dir
# Be sure not to overwrite anything...
%defattr(-,geoserver,geoserver,-)
%config(noreplace) %{_localstatedir}/lib/%{name}/*

%changelog

