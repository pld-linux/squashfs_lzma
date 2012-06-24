#
# NOTE: squashfs 3.1 uses some zlib functions which don't exist in lzma,
#	that's why it probably won't be updated
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if !%{with kernel}
%undefine	with_dist_kernel
%endif

%define	_origname	squashfs
%define		_rel	1
Summary:	Set of tools which creates squashfs filesystem with lzma compression
Summary(pl.UTF-8):   Zestaw narzędzi do tworzenia systemu plików squashfs z kompresją lzma
Name:		squashfs_lzma
Version:	3.0
Release:	%{_rel}
License:	GPL
Group:		Base/Utilities
Source0:	http://dl.sourceforge.net/squashfs/%{_origname}%{version}.tar.gz
# Source0-md5:	9fd05d0bfbb712f5fb95edafea5bc733
Patch0:		%{name}-module.patch
Patch1:		%{name}-not_zlib.patch
Patch2:		%{name}-magic.patch
URL:		http://squashfs.sourceforge.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.330
%endif
%if %{with userspace}
BuildRequires:	libstdc++-devel
BuildRequires:	lzma-devel >= 4.43-5
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package contains utilities for squashfs filesystem with lzma
compression.

Squashfs is a highly compressed read-only filesystem for Linux (kernel
2.4.x and 2.6.x). It uses lzma compression to compress files, inodes
and directories. Inodes in the system are very small and all blocks
are packed to minimise data overhead. Block sizes greater than 4K are
supported up to a maximum of 64K.

Squashfs is intended for general read-only filesystem use, for
archival use (i.e. in cases where a .tar.gz file may be used), and in
constrained block device/memory systems (e.g. embedded systems) where
low overhead is needed.

%description -l pl.UTF-8
Zestaw narzędzi do tworzenia systemu plików squashfs z kompresją lzma.

Squashfs jest systemem plików tylko do odczytu z dużym współczynnikiem
kompresji dla Linuksa (jądra 2.4.x i 2.6.x). Używa kompresji lzma do
plików, i-węzłów oraz katalogów. I-węzły są bardzo małe, a wszystkie
bloki są pakowane, aby zmniejszyć objętość. Rozmiary bloków powyżej
4kB są obsługiwane - maksymalnie do 64kB.

Squashfs ma służyć jako system plików tylko do odczytu ogólnego
przeznaczenia, do składowania archiwów (w tych przypadkach, kiedy
można używać plików .tar.gz) oraz w systemach z dużymi ograniczeniami
pamięci i urządzeń blokowych (np. systemach wbudowanych).

%package -n kernel%{_alt_kernel}-fs-squashfs_lzma
Summary:	Linux driver for lzma-compressed squashfs
Summary(pl.UTF-8):   Sterownik dla Linuksa do squashfs skompresowanego lzma
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel%{_alt_kernel}-fs-squashfs_lzma
This is driver for lzma-compressed squashfs for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-fs-squashfs_lzma -l pl.UTF-8
Sterownik dla Linuksa do squashfs skompresowanego lzma.

Ten pakiet zawiera moduł jądra Linuksa.

%package -n kernel%{_alt_kernel}-smp-fs-squashfs_lzma
Summary:	Linux SMP driver for MODULE_NAME
Summary(pl.UTF-8):   Sterownik dla Linuksa SMP do MODULE_NAME
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel%{_alt_kernel}-smp-fs-squashfs_lzma
This is driver for lzma-compressed squashfs for Linux.

This package contains Linux SMP module.

%description -n kernel%{_alt_kernel}-smp-fs-squashfs_lzma -l pl.UTF-8
Sterownik dla Linuksa do squashfs skompresowanego lzma.

Ten pakiet zawiera moduł jądra Linuksa SMP.

%prep
%setup -q -n %{_origname}%{version}
%patch0 -p0
%patch1 -p1
%patch2 -p1

%build
%if %{with userspace}
%{__make} -C squashfs-tools \
	CC="%{__cc}" \
	CXX="%{__cxx}" \
	CFLAGS="-I. %{rpmcflags}"
%endif

%if %{with kernel}
%build_kernel_modules -C squashfs -m squashfs_lzma
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_sbindir}
install squashfs-tools/mksquashfs $RPM_BUILD_ROOT%{_sbindir}/mksquashfs_lzma
install squashfs-tools/unsquashfs $RPM_BUILD_ROOT%{_sbindir}/unsquashfs_lzma
%endif

%if %{with kernel}
%install_kernel_modules -m squashfs/squashfs_lzma -d kernel/fs
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-fs-squashfs_lzma
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-fs-squashfs_lzma
%depmod %{_kernel_ver}

%post	-n kernel%{_alt_kernel}-smp-fs-squashfs_lzma
%depmod %{_kernel_ver}smp

%postun	-n kernel%{_alt_kernel}-smp-fs-squashfs_lzma
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README ACKNOWLEDGEMENTS CHANGES
%attr(755,root,root) %{_sbindir}/*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-fs-squashfs_lzma
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/fs/squashfs_lzma.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-fs-squashfs_lzma
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/fs/squashfs_lzma.ko*
%endif
%endif
