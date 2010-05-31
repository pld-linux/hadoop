# TODO
# - make use offline maven
# - hadoop-fuse?
# - hadoop-native.spec?
# - pick snippets from http://issues.apache.org/jira/browse/HADOOP-5615
# - http://issues.apache.org/jira/browse/HADOOP-6255
# - https://wiki.ubuntu.com/HadoopPackagingSpec
Summary:	Hadoop Distributed File System and MapReduce implementation
Name:		hadoop
Version:	0.20.2
Release:	0.1
License:	Apache v2.0
Group:		Daemons
URL:		http://hadoop.apache.org/common/
Source0:	http://www.apache.org/dist/hadoop/core/%{name}-%{version}/hadoop-%{version}.tar.gz
# Source0-md5:	8f40198ed18bef28aeea1401ec536cb9
BuildRequires:	ant
BuildRequires:	jdk
BuildRequires:	jpackage-utils
BuildRequires:	rpmbuild(macros) >= 1.202
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	jpackage-utils
Requires:	jre
Provides:	group(hadoop)
Provides:	user(hadoop)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir		%{_datadir}/%{name}

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
	# set JAVA_HOME from jpackage-utils
	s|.*JAVA_HOME=.*|. %{_javadir}-utils/java-functions; set_jvm|
	s|.*HADOOP_CLASSPATH=.*|export HADOOP_CLASSPATH=$HADOOP_CONF_DIR:$(build-classpath hadoop)|
	s|.*HADOOP_LOG_DIR=.*|export HADOOP_LOG_DIR=%{_var}/log/hadoop|
	s|.*HADOOP_PID_DIR=.*|export HADOOP_PID_DIR=%{_var}/run/hadoop|
' conf/hadoop-env.sh

%build
%ant package \
	-Dversion=%{version} \
%if %{with apidocs}
	-Djava5.home=%{java_home} \
	-Dforrest.home=../apache-forrest-0.8
%else
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_appdir},%{_var}/{log,run}/hadoop}
%if 0
cp -a bin c++ conf ivy lib webapps $RPM_BUILD_ROOT%{_appdir}
cp -a *.jar *.xml $RPM_BUILD_ROOT%{_appdir}

# we're noarch
rm -rvf $RPM_BUILD_ROOT%{_appdir}/lib/native/
rm -rvf $RPM_BUILD_ROOT%{_appdir}/c++/Linux-amd64-64
rm -rvf $RPM_BUILD_ROOT%{_appdir}/c++/Linux-i386-32
rm -rvf $RPM_BUILD_ROOT%{_appdir}/librecordio/librecordio.a
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 245 -r hadoop
%useradd -u 245 -m -r -g hadoop -c 'HDFS Runtime User' -s /bin/sh hadoop

%postun
if [ "$1" = "0" ]; then
	%userremove hadoop
	%groupremove hadoop
fi

%files
%defattr(644,root,root,755)
%doc CHANGES.txt NOTICE.txt README.txt
%dir %{_appdir}
%dir %{_appdir}/bin
%attr(755,root,root) %{_appdir}/bin/*
%dir %{_appdir}/conf
%config(noreplace) %verify(not md5 mtime size) %{_appdir}/conf/*
%{_appdir}/webapps

%{_appdir}/hadoop-*.jar
%{_appdir}/ivy
%{_appdir}/ivy.xml
%dir %{_appdir}/lib
%{_appdir}/lib/jdiff
%{_appdir}/lib/*.jar
%{_appdir}/lib/jsp-2.1

%attr(775,root,hadoop) %{_var}/run/hadoop
%attr(775,root,hadoop) %{_var}/log/hadoop
