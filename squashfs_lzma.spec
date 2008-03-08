#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif

%define		_origname	squashfs
%define		_rel	0.1
Summary:	Set of tools which creates squashfs filesystem with lzma compression
Summary(pl.UTF-8):	Zestaw narzędzi do tworzenia systemu plików squashfs z kompresją lzma
Name:		squashfs_lzma
Version:	3.3
Release:	%{_rel}
License:	GPL
Group:		Base/Utilities
Source0:	http://www.squashfs-lzma.org/dl/squashfs%{version}.tar.gz
# Source0-md5:	62d3ff7c067a5aa82f57711b3a4ab86a
Source1:	http://www.squashfs-lzma.org/dl/lzma457.tar.bz2
# Source1-md5:	fc7a12a396ade1772e959604d6eb31e1
Source2:	http://www.squashfs-lzma.org/dl/sqlzma%{version}-457.tar.bz2
# Source2-md5:	27cc878dca09d955fcc63cb671e55846
Patch0:		http://www.squashfs-lzma.org/dl/squashfs-cvsfix.patch
#Patch1:	%{name}-not_zlib.patch
#Patch2:	%{name}-magic.patch
URL:		http://www.squashfs-lzma.org/
BuildRequires:	patchutils
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.24.3}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
%if %{with userspace}
BuildRequires:	libstdc++-devel
#BuildRequires:	lzma-devel >= 4.43-5
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
Summary(pl.UTF-8):	Sterownik dla Linuksa do squashfs skompresowanego lzma
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-fs-squashfs_lzma
This is driver for lzma-compressed squashfs for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-fs-squashfs_lzma -l pl.UTF-8
Sterownik dla Linuksa do squashfs skompresowanego lzma.

Ten pakiet zawiera moduł jądra Linuksa.

%prep
%setup -q -n %{_origname}%{version} -a1 -a2
%patch0 -p1
%{__patch} -p1 < sqlzma1-449.patch
%{__patch} -p1 < sqlzma2u-3.3.patch

# in this patch all are new files except init/do_mounts_rd.c:
filterdiff -i '*/fs/squashfs/*' -i '*/include/linux/*' < kernel-patches/linux-2.6.24/squashfs3.3-patch | %{__patch} -p1
%{__patch} -p1 < sqlzma2k-3.3.patch
ln -s ../../sqlzma.h fs/squashfs
ln -s ../../sqmagic.h fs/squashfs

#%patch1 -p1
#%patch2 -p1

%build
%if %{with userspace}
topdir=$(pwd)
%{__make} -C C/Compress/Lzma -f sqlzma.mk Sqlzma=$topdir \
	CXX="%{__cxx}" \
	CXX_C="%{__cc}" \
	CC="%{__cc}" \
	OPTFLAGS="%{rpmcflags}" \
	LDFLAGS="%{rpmcflags} %{rpmldflags}"

%{__make} -C CPP/7zip/Compress/LZMA_Alone -f sqlzma.mk Sqlzma=$topdir \
	CXX="%{__cxx}" \
	CXX_C="%{__cc}" \
	CC="%{__cc}" \
	OPTFLAGS="%{rpmcflags}" \
	LDFLAGS="%{rpmcflags} %{rpmldflags}"

%{__make} -C squashfs-tools Sqlzma=$topdir \
	LzmaAlone=../CPP/7zip/Compress/LZMA_Alone \
	LzmaC=../C/Compress/Lzma \
	CC="%{__cc}" \
	CXX="%{__cxx}" \
	DebugFlags="%{rpmcflags}"
%endif

%if %{with kernel}
%build_kernel_modules -C fs/squashfs -m squashfs
mv fs/squashfs/squashfs{,_lzma}-dist.ko
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_sbindir}
install squashfs-tools/mksquashfs $RPM_BUILD_ROOT%{_sbindir}/mksquashfs_lzma
install squashfs-tools/unsquashfs $RPM_BUILD_ROOT%{_sbindir}/unsquashfs_lzma
%endif

%if %{with kernel}
%install_kernel_modules -m fs/squashfs/squashfs_lzma -d kernel/fs
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-fs-squashfs_lzma
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-fs-squashfs_lzma
%depmod %{_kernel_ver}

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
%endif
