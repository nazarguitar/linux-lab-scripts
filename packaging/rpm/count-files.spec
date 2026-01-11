Name:           count-files
Version:        2.0
Release:        1%{?dist}
Summary:        Script to count regular files in a directory

License:        MIT
URL:            https://github.com/nazarguitar/linux-lab-scripts
Source0:        %{name}-%{version}.tar.gz
Source1:        count_files.1
Source2:        count_files.conf
BuildArch:      noarch
Requires:       bash
Requires:       coreutils
Requires:       findutils

%description
A Bash script that counts the number of regular files
in a directory. Version 2.0 adds a configuration file
and support for passing a directory as parameter (-d DIR).

%prep
%setup -q

%build

%install
# Install script
mkdir -p %{buildroot}%{_bindir}
install -m 755 count_files.sh %{buildroot}%{_bindir}/count_files

# Install man page
mkdir -p %{buildroot}%{_mandir}/man1
install -m 644 %{SOURCE1} %{buildroot}%{_mandir}/man1/count_files.1

# Install configuration file
mkdir -p %{buildroot}%{_sysconfdir}/count-files
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/count-files/count_files.conf

%pre
echo "Preparing to install count-files..."

%post
echo "count-files installed successfully."
echo "Try: man count_files"
echo "Config located at /etc/count-files/count_files.conf"

%files
%{_bindir}/count_files
%{_mandir}/man1/count_files.1*
%config(noreplace) %{_sysconfdir}/count-files/count_files.conf

%changelog
* Sun Jan 11 2026 nazarguitar <usimvmukr.net@gmail.com> - 2.0-1
- Added config file support, -d option, man page, %pre and %post scripts

* Thu Dec 18 2025 nazarguitar <usimvmukr.net@gmail.com> - 1.0-1
- Initial package release

