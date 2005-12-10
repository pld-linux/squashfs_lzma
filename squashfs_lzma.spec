#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif

%define	_origname	squashfs
Summary:	Set of tools which creates squashfs filesystem with lzma compression
Summary(pl):	Zestaw narzêdzi do tworzenia systemu plików squashfs z kompresja lzma
Name:		squashfs_lzma
Version:	2.2
%define		_rel	0.1
Release:	%{_rel}
License:	GPL
Group:		Base/Utilities
Source0:	http://dl.sourceforge.net/squashfs/%{_origname}%{version}-r2.tar.gz
# Source0-md5:	a8d09a217240127ae4d339e8368d2de1
Patch0:		%{name}-module.patch
Patch1:		%{name}-not_zlib.patch
URL:		http://squashfs.sourceforge.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.217
%endif
%if %{with userspace}
BuildRequires:	libstdc++-devel
BuildRequires:	lzma-devel
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This package contains utilities for squashfs filesystem.

Squashfs is a highly compressed read-only filesystem for Linux (kernel
2.4.x and 2.6.x). It uses zlib compression to compress both files,
inodes and directories. Inodes in the system are very small and all
blocks are packed to minimise data overhead. Block sizes greater than
4K are supported up to a maximum of 64K.

Squashfs is intended for general read-only filesystem use, for
archival use (i.e. in cases where a .tar.gz file may be used), and in
constrained block device/memory systems (e.g. embedded systems) where
low overhead is needed.

%description -l pl
Zestaw narzêdzi do tworzenia systemu plików squashfs.

Squashfs jest systemem plików tylko do odczytu z du¿ym wspó³czynnikiem
kompresji dla Linuksa (j±dra 2.4.x i 2.6.x). U¿ywa kompresji zlib do
plików, i-wêz³ów oraz katalogów. I-wêz³y s± bardzo ma³e, a wszystkie
bloki s± pakowane, aby zmniejszyæ objêto¶æ. Rozmiary bloków powy¿ej
4kB s± obs³ugiwane - maksymalnie do 64kB.

Squashfs ma s³u¿yæ jako system plików tylko do odczytu ogólnego
przeznaczenia, do sk³adowania archiwów (w tych przypadkach, kiedy
mo¿na u¿ywaæ plików .tar.gz) oraz w systemach z du¿ymi ograniczeniami
pamiêci i urz±dzeñ blokowych (np. systemach wbudowanych).

%package -n kernel-fs-squashfs_lzma
Summary:	Linux driver for lzma-compressed squashfs
Summary(pl):	Sterownik dla Linuksa do squashfs skompresowanego lzma
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-fs-squashfs_lzma
This is driver for lzma-compressed squashfs for Linux.

This package contains Linux module.

%description -n kernel-fs-squashfs_lzma -l pl
Sterownik dla Linuksa do squashfs skompresowanego lzma.

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel-smp-fs-squashfs_lzma
Summary:	Linux SMP driver for MODULE_NAME
Summary(pl):	Sterownik dla Linuksa SMP do MODULE_NAME
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel-smp-fs-squashfs_lzma
This is driver for lzma-compressed squashfs for Linux.

This package contains Linux SMP module.

%description -n kernel-smp-fs-squashfs_lzma -l pl
Sterownik dla Linuksa do squashfs skompresowanego lzma.

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -q -n %{_origname}%{version}-r2
%patch0 -p0
%patch1 -p1

%build
%if %{with userspace}
%{__make} -C squashfs-tools \
	CC="%{__cc}" \
	CFLAGS="-I. %{rpmcflags}"
%endif

%if %{with kernel}
cd squashfs
# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
%ifarch ppc
	if [ -d "%{_kernelsrcdir}/include/asm-powerpc" ]; then
		install -d include/asm
		cp -a %{_kernelsrcdir}/include/asm-%{_target_base_arch}/* include/asm
		cp -a %{_kernelsrcdir}/include/asm-powerpc/* include/asm
	else
		ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	fi
%else
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
%endif
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	touch include/config/MARKER
#
#	patching/creating makefile(s) (optional)
#
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}

	mv squashfs_lzma{,-$cfg}.ko
done
cd ..
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -D squashfs-tools/mksquashfs $RPM_BUILD_ROOT%{_sbindir}/mksquashfs_lzma
%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/fs
install squashfs/squashfs_lzma-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/fs/squashfs_lzma.ko
%if %{with smp} && %{with dist_kernel}
install squashfs/squashfs_lzma-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/fs/squashfs_lzma.ko
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-fs-squashfs_lzma
%depmod %{_kernel_ver}

%postun	-n kernel-fs-squashfs_lzma
%depmod %{_kernel_ver}

%post	-n kernel-smp-fs-squashfs_lzma
%depmod %{_kernel_ver}smp

%postun	-n kernel-smp-fs-squashfs_lzma
%depmod %{_kernel_ver}smp

%if %{with kernel}
%files -n kernel-fs-squashfs_lzma
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/fs/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-fs-squashfs_lzma
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/fs/*.ko*
%endif
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README ACKNOWLEDGEMENTS CHANGES
%attr(755,root,root) %{_sbindir}/*
%endif
