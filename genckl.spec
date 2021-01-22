%define name genckl
%define version 0.1
%define _prefix /usr/local
%define python3_sitelib %(python3 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(prefix='%{_prefix}'))")

Name: %{name}
Version: %{version}
Release: 1
Summary: Generate a ckl file based on STIG zip and/or xccdf file(s)
License: GPLv3
Url: https://github.com/ap1x/%{name}
Source0: %{name}-%{version}.tar.gz
Group: Applications/File
BuildArch: noarch
Provides: %{_bindir}/%{name}
BuildRequires: python3 >= 3.6
Requires: python3 >= 3.6
AutoReq: no

%description
The %{name} utility generates a STIG Viewer checklist (ckl) file based on one or 
more input files, which can be either STIG formatted zip, or xccdf formatted 
xml. If xccdf results are found in any of the input files, they are included in 
the output checklist. Optionally supports checklist templates and automatic 
host data collection.

%prep
%setup

%build
python3 setup.py build
python3 setup.py build_sphinx --builder man

%install
python3 setup.py install --prefix=%{_prefix} --root=%{buildroot}
mkdir -p %{buildroot}/%{_mandir}/man1
gzip -c build/sphinx/man/%{name}.1 > %{buildroot}/%{_mandir}/man1/%{name}.1.gz

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%license LICENSE
%{python3_sitelib}/%{name}*
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1.gz
