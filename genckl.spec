%define name genckl
%define version 0.1
%define _prefix /usr/local

Name: %{name}
Version: %{version}
Release: 1
Summary: Generate a ckl file based on STIG zip and/or xccdf file(s)
License: GPLv3
Url: https://github.com/ap1x/genckl
Source0: %{name}-%{version}.tar.gz
Group: Applications/File
BuildArch: noarch

%description
The genckl utility generates a STIG Viewer checklist (ckl) file based on one or more input files, which can be either STIG formatted zip, or xccdf formatted xml. If xccdf results are found in one of the input files, they are included in the output checklist. Optionally supports checklist templates and automatic host data collection.

%prep
%setup

%build
python3 setup.py build
python3 setup.py build_sphinx --builder man

%install
python3 setup.py install --prefix %{_prefix} --root=%{buildroot} --record=INSTALLED_FILES
mkdir -p %{buildroot}/%{_mandir}/man1
gzip -c build/sphinx/man/genckl.1 > %{buildroot}/%{_mandir}/man1/genckl.1.gz

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%license LICENSE
%{_mandir}/man1/genckl.1.gz
%defattr(-,root,root)
