#!/usr/bin/perl
$\=$/;
use CGI qw(:all);
use Digest::SHA qw(sha256_base64);

$authfile='/authstr_sha256'; #sha256 hashes of auth strs. one per line
$maxfilesize=40; #MB
$uploaddir='upload/';
$logfile='/var/log/ructf2011_upload.log';


sub check_authstr
{
    my $s=shift;
    open $f,$authfile or die "Can't open file '$file' : $!";
    while(<$f>)
    {
	chomp;
	$authstr{$_}=1;
    }
    close $f;
    return 1 if(exists $authstr{sha256_base64($s)});
    return 0;
}

sub bad_param_str
{
    print h2("Bad auth str :(");
    print end_html();
    exit(0);
}

sub slog
{
    open LOG,">>$logfile" or die "Can't open log file : $!";
    print LOG scalar localtime, " $$ | ", shift;
    close LOG;
}

sub got_file
{
    my $m=$maxfilesize*1024*1024;
    bad_param_str if(!check_authstr(param('authstr')));
    my $f=upload('upload_file');
    @f=stat $f;
    print "Filesize: $f[7]<br>";
    if ($f[7]>$m)
    {
	print "<font color=red>Max filesize: $maxfilesize MB</font>";
	print end_html();
	exit(0);
    }
    my $outname=`pwgen -c -n -s 40 1`;
    chomp $outname;
    while (-f "$uploaddir/$outname")
    {
	$outname=`pwgen -c -n -s 40 1`;
	chomp $outname;
    }
    open $o,">$uploaddir/$outname" or die "Can't open file '$uploaddir/$outname' : $!";
    binmode $o;
    binmode $f;
    while(read($f,$msg,1024*1024)!=0)
    {
	syswrite($o,$msg);
    }
    close $o;
    slog($ENV{REMOTE_ADDR} . ' ' . param('authstr') . ' \'' . param('upload_file') . "' $outname $f[7]");
    print "Filename: '$outname'<br>";
    print "Successful uploaded!<br>"
}

sub file_form
{
    print start_multipart_form('POST');
    print 'Authstr: ', textfield(-name=>'authstr',
		    -size=>50,
		    -maxlength=>80);
    print filefield(-name=>'upload_file',
                    -size=>20);
    print submit(-name=>'q',
	            -value=>'Upload') . '<br>';
    endform();	
    print "<br>";
    print "Max filesize: $maxfilesize MB";
}

print header(-charset=>'utf8',-type=>'text/html');
print start_html(-encoding=>'UTF-8',-lang=>'ru_RU',-title=>'RuCTF 2011 Quals Upload Service',-style=>{-src=>'qserver.css'}),
    h1('RuCTF 2011 Quals Upload Service');

if(defined param('q'))
{
    got_file();
}else
{
    file_form();
}
print end_html();