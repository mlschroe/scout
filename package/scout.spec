#
# spec file for package scout
#
# Copyright (c) 2010 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# norootforbuild

Name:           scout
Version:        0.1.0
Release:        35
Url:            http://old-en.opensuse.org/Scout
Summary:        Indexing Package Properties
License:        MIT
Group:          System/Packages
Source:         %{name}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  gettext
BuildRequires:  python
BuildRequires:  rpm-python
Requires:       python

%if 0%{?suse_version}
BuildRequires:  python-xml
Requires:       python-xml
%if 0%{?suse_version} >= 1120
BuildArch:      noarch
%else
%define python_sitelib %{py_sitedir}
%endif
%if 0%{?suse_version} > 1100
BuildRequires:  python-solv
Requires:       python-solv >= 0.6.0
%endif
%else
BuildArch:      noarch
%endif

%description
The scout tool helps with indexing of various package properties.


%define scoutrepo none
%define cnfrepo none

%if 0%{?suse_version} > 1120
%define scoutrepo suse113
%define cnfrepo zypp
%endif
%if 0%{?suse_version} <= 1120 && 0%{?suse_version} > 1110
%define scoutrepo suse112
%define cnfrepo zypp
%endif
%if 0%{?suse_version} <= 1110 && 0%{?suse_version} > 1100
%define scoutrepo suse111
%define cnfrepo zypp
%endif
%if 0%{?suse_version} <= 1100 && 0%{?suse_version} > 1030
%define scoutrepo suse110
%define cnfrepo suse110
%endif
%if 0%{?suse_version} <= 1030 && 0%{?suse_version} > 1020
%define scoutrepo suse103
%define cnfrepo suse103
%endif
%if 0%{?sles_version} == 10
%define scoutrepo sle10
%define cnfrepo sle10
%endif

%if %{cnfrepo} != none

%package -n command-not-found
Version:        0.1.0
Release:        42
Summary:        Command Not Found extension for shell
Group:          System/Packages
Requires:       python rpm-python
Requires:       scout = %{version}-%{release}
%if 0%{?suse_version} && 0%{?suse_version} <= 1100
Requires:       bash(CommandNotFound)
%endif
%if %{cnfrepo} != zypp
Requires:       scout-bin-%{cnfrepo}
%endif

%description -n command-not-found
The "command not found" message is not very helpful. If e.g. the unzip
command is not found but it's available in a package, it would be very
interesting if the system could tell that the command is currently not
available, but installing a package would provide it.



%endif

# %if %{scoutrepo} != none
# 
# %package -n python-import-error
# Version:        0.1.0
# Release:        1
# License:        X11/MIT
# Group:          System/Packages
# Summary:        Import Error extension for python interpretter
# Requires:       scout = %{version}-%{release}
# Requires:       python(ImportError)
# Requires:       scout-python-%{scoutrepo}
# 
# %description -n python-import-error
# The "Import Error exception" is not really helpfull (as a "command not found"
# in shell). This package contains an ImportError exception handler called by
# (patched) Python interpreter, which could tell to the user, where the missing
# Python module is.
# 
# %endif

%prep
%setup -q -n %{name}

%build
# compile scripts
python -mcompileall .

%install
# --- scout ---
# install python scripts
mkdir -p $RPM_BUILD_ROOT%{python_sitelib}/%{name}
shopt -s extglob
cp -a scout/!(foo).py{,c} $RPM_BUILD_ROOT%{python_sitelib}/%{name}
# install data files
install -D -m 0644 repos.conf $RPM_BUILD_ROOT%{_datadir}/%{name}/repos.conf
# install scout binary
install -D -m 0755 scout-cmd.py $RPM_BUILD_ROOT%{_bindir}/%{name}
# install bash completion
install -D -m 0644 scout-bash-completion $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/scout.sh
# install manpage
install -D -m 0644 doc/scout.1 $RPM_BUILD_ROOT%{_mandir}/man1/scout.1
# install and find languages
for po in i18n/scout/*.po; do
    pofile=${po##*/}
    lang=${pofile%.po}
    msgfmt $po -o i18n/scout/$lang.mo
    install -D -m 0644 i18n/scout/$lang.mo $RPM_BUILD_ROOT%{_datadir}/locale/$lang/LC_MESSAGES/scout.mo
done
%find_lang scout

%if %{cnfrepo} != none
# --- command-not-found ---
install -D -m 0755 handlers/bin/command-not-found $RPM_BUILD_ROOT%{_bindir}/command-not-found
ln -sf command-not-found $RPM_BUILD_ROOT%{_bindir}/cnf
# install manpage
install -D -m 0644 doc/command-not-found.1 $RPM_BUILD_ROOT%{_mandir}/man1/command-not-found.1
ln -sf command-not-found.1.gz $RPM_BUILD_ROOT%{_mandir}/man1/cnf.1.gz
# install shell handlers
for shell in bash zsh; do
    install -D -m 644 handlers/bin/command_not_found_${shell} $RPM_BUILD_ROOT%{_sysconfdir}/${shell}_command_not_found
    sed -i 's:__REPO__:%{cnfrepo}:' $RPM_BUILD_ROOT%{_sysconfdir}/${shell}_command_not_found
done
# install and find languages
for po in i18n/command-not-found/*.po; do
    pofile=${po##*/}
    lang=${pofile%.po}
    msgfmt $po -o i18n/command-not-found/$lang.mo
    install -D -m 0644 i18n/command-not-found/$lang.mo $RPM_BUILD_ROOT%{_datadir}/locale/$lang/LC_MESSAGES/command-not-found.mo
done
%find_lang command-not-found
%endif

# %if %{scoutrepo} != none
# # --- python-import-error ---
# install -D -m 0755 handlers/python/python_import_error_handler $RPM_BUILD_ROOT/%{python_sitelib}/python_import_error_handler
# %endif

%clean
rm -rf $RPM_BUILD_ROOT

%files -f scout.lang
%defattr(-,root,root)
%doc AUTHORS LICENSE README TODO doc/scout.html doc/scout.pdf
%{_bindir}/%{name}*
%{python_sitelib}/%{name}
%{_datadir}/%{name}
%config %{_sysconfdir}/bash_completion.d/*
%{_mandir}/man1/scout*

%if %{cnfrepo} != none

%files -n command-not-found -f command-not-found.lang
%defattr(-,root,root)
%doc handlers/bin/README
%{_bindir}/cnf
%{_bindir}/command-not-found
%config %{_sysconfdir}/*_command_not_found
%{_mandir}/man1/cnf*
%{_mandir}/man1/command-not-found*

%endif

# %if %{scoutrepo} != none
# 
# %files -n python-import-error
# %defattr(-,root,root)
# %{python_sitelib}/python_import_error_handler
# 
# %endif

%changelog
