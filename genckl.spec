%define name genckl
%define version 0.1

%define prefix %{_prefix}/local
%define mandir %{prefix}/share/man

Name: %{name}
Version: %{version}
Release: 1
Summary: Generate a STIG Viewer checklist file
License: GPLv3
Url: https://github.com/ap1x/genckl
Source0: %{name}-%{version}.tar.gz
Group: Applications/File
BuildArch: noarch
Vendor: ap1x

%description
This utility generates a ckl file from xccdf or zip file(s).
Supports multiple input files, xccdf results, automatic host
data collection, and more.

%prep
%setup

%build
python3 setup.py build
python3 setup.py build_sphinx --builder man

%install
python3 setup.py install --prefix %{prefix} --single-version-externally-managed -O1 --root=%{buildroot} --record=INSTALLED_FILES
mkdir -p %{buildroot}/%{mandir}/man1
gzip -c build/sphinx/man/genckl.1 > %{buildroot}/%{mandir}/man1/genckl.1.gz

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%license LICENSE
%{mandir}/man1/genckl.1.gz
%defattr(-,root,root)
