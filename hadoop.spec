# TODO
# - hadoop-fuse?
# - pick snippets from http://issues.apache.org/jira/browse/HADOOP-5615
# - http://issues.apache.org/jira/browse/HADOOP-6255
# - https://wiki.ubuntu.com/HadoopPackagingSpec
Summary:	Hadoop Distributed File System and MapReduce implementation
Name:		hadoop
Version:	0.20.1
Release:	0.1
License:	ASL 2.0
Group:		Daemons
URL:		http://hadoop.apache.org/common/
Source0:	http://www.apache.org/dist/hadoop/core/%{name}-%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	719e169b7760c168441b49f405855b72
BuildRequires:	rpmbuild(macros) >= 1.202
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	jdk
Provides:	group(hadoop)
Provides:	user(hadoop)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Apache Hadoop Core is a software platform that lets one easily write
and run applications that process vast amounts of data.

Here's what makes Hadoop especially useful:
 - Scalable: Hadoop can reliably store and process petabytes.
 - Economical: It distributes the data and processing across clusters
   of commonly available computers. These clusters can number into the
   thousands of nodes.
 - Efficient: By distributing the data, Hadoop can process it in
   parallel on the nodes where the data is located. This makes it
   extremely rapid.
 - Reliable: Hadoop automatically maintains multiple copies of data and
   automatically redeploys computing tasks based on failures.

Hadoop implements MapReduce, using the Hadoop Distributed File System
(HDFS). MapReduce divides applications into many small blocks of work.
HDFS creates multiple replicas of data blocks for reliability, placing
them on compute nodes around the cluster. MapReduce can then process
the data where it is located.

%prep
%setup -q

# hadoop-env.sh defaults
%{__sed} -i -e '
s|.*JAVA_HOME=.*|export JAVA_HOME=%{_prefix}/java/latest|
	s|.*HADOOP_CLASSPATH=.*|export HADOOP_CLASSPATH=$HADOOP_CONF_DIR:$(build-classpath hadoop)|
	s|.*HADOOP_LOG_DIR=.*|export HADOOP_LOG_DIR=%{_var}/log/hadoop|
	s|.*HADOOP_PID_DIR=.*|export HADOOP_PID_DIR=%{_var}/run/hadoop|
' conf/hadoop-env.sh

%build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_prefix}/local/%{name}
for D in $(find . -mindepth 1 -maxdepth 1 -type d | cut -c 3- | %{__grep} -Evw 'build|docs|src'); do
	%{__cp} -a $D $RPM_BUILD_ROOT%{_prefix}/local/%{name}/
done
install *.jar $RPM_BUILD_ROOT%{_prefix}/local/%{name}/
install *.txt $RPM_BUILD_ROOT%{_prefix}/local/%{name}/
install *.xml $RPM_BUILD_ROOT%{_prefix}/local/%{name}/
install -d $RPM_BUILD_ROOT%{_var}/run/hadoop
install -d $RPM_BUILD_ROOT%{_var}/log/hadoop

# Packing list
(	cd $RPM_BUILD_ROOT
	echo '%defattr(-,root,root,-)'
	echo '%attr(0755,hadoop,hadoop) %{_var}/run/hadoop'
	echo '%attr(0755,hadoop,hadoop) %{_var}/log/hadoop'
	find $RPM_BUILD_ROOT%{_prefix}/local/%{name} -type d -printf '%%%dir %p\n' | %{__sed} -e 's|$RPM_BUILD_ROOT||g'
	find $RPM_BUILD_ROOT%{_prefix}/local/%{name} -type f -printf '%p\n' | %{__grep} -v 'conf/' | %{__sed} -e 's|$RPM_BUILD_ROOT||g'
	find $RPM_BUILD_ROOT%{_prefix}/local/%{name}/conf -type f -printf '%%%config(noreplace) %p\n' | %{__sed} -e 's|$RPM_BUILD_ROOT||g'
) > filelist

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -r hadoop
%useradd -m -r -g hadoop -c 'HDFS Runtime User' -s /bin/sh hadoop

%files -f filelist
%defattr(644,root,root,755)
