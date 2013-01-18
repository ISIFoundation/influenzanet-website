#!/usr/bin/perl -w
# -- extract cohort information from csv with data form cohorts.sql query
# -- reads STDIN, relies on a header and a table sorted last by vaccination
#    (so that matched groups are in subsequent lines)
# -- needs a column called "vaccinated" and can use columns called
#    "week" and "year"
# -- also needs a column called "ili" and a column called "non_ili"
# -- every column right of the "vaccinated" column will be ignored for the
#    group matching (these columns should contain the data)

use strict;

sub min {
    [$_[0], $_[1]]->[$_[0] >= $_[1]];
}

my $motionchart = 0; # motion chart format
my $countries = 0; # separate countries (otherwise they are matched)

foreach (@ARGV) {
    if ($_ eq "-m") {
	$motionchart = 1;
    }
    if ($_ eq "-c") {
	$countries = 1;
    }
}

# read header line
my $header_line;
if (!($header_line = <STDIN>)) {
    die "No header line\n";
}
chomp($header_line);
my @header = split /,/, $header_line;
my $country_index = -1; # index of "country" column
my $vaccinated_index = -1; # index of "vaccinated" column
my $week_index = -1; # index of "week" column
my $year_index = -1; # index of "year" column
my $yearweek_index = -1; # index of "year-week" column
my $ili_index = -1; # index of "ili" coulmn
my $nonili_index = -1; # index of "nonili" coulmn
my $count = -1;
my $sum = 0;

# find where the relevant columns are
for (my $i = 0; $i < scalar(@header); $i++) {
    if ("$header[$i]" eq "country") {
	$country_index = $i;
    }
    if ("$header[$i]" eq "vaccinated") {
	$vaccinated_index = $i;
    }
    if ("$header[$i]" eq "week") {
	$week_index = $i;
    }
    if ("$header[$i]" eq "year") {
	$year_index = $i;
    }
    if ("$header[$i]" eq "year-week") {
	$yearweek_index = $i;
    }
    if ("$header[$i]" eq "ili") {
	$ili_index = $i;
    }
    if ("$header[$i]" eq "non_ili") {
	$nonili_index = $i;
    }
}

if ($countries && $country_index == -1) {
    die "Input has no \"country\" column\n";
}
if ($vaccinated_index == -1) {
    die "Input has no \"vaccinated\" column\n";
}
if ($ili_index == -1) {
    die "Input has no \"ili\" column\n";
}
if ($nonili_index == -1) {
    die "Input has no \"non_ili\" column\n";
}
if ((($year_index == -1) || ($week_index == -1)) &&
	$yearweek_index == -1) {
    die "Input has no year/week columns\n";
}
if ($countries && $motionchart) {
    die "Cannot split motionchart by countries\n";
}

my @data; # will store the data read in from csv
my @nextdata; # will store one readahead from csv
if (!(@nextdata = split /,/, <STDIN>)) {
    die "No data\n";
}

# variables to store counts of vaccinated/unvaccinated
my %vaccinated_ili;
my %vaccinated_nonili;
my %unvaccinated_ili;
my %unvaccinated_nonili;

while (<STDIN>) {
    @data = @nextdata;
    chomp;
    @nextdata = split /,/;

    my $week = 0;
    my $year = 0;

    if ($week_index >= 0 && $year_index >= 0) {
	#  we have got a "week" and "year" column
	$week = $data[$week_index];
	$year = $data[$year_index];
    } else {
	#  we have got a "year-week" column
	($year, $week) = split /-/, $data[$yearweek_index];
    }
    if ($countries) {
	my $country = $data[$country_index];
	if (!(exists $vaccinated_ili{$country}{$year}{$week})) {
	    $vaccinated_ili{$country}{$year}{$week} = 0;
	}
	if (!(exists $vaccinated_nonili{$country}{$year}{$week})) {
	    $vaccinated_nonili{$country}{$year}{$week} = 0;
	}
	if (!(exists $unvaccinated_ili{$country}{$year}{$week})) {
	    $unvaccinated_ili{$country}{$year}{$week} = 0;
	}
	if (!(exists $unvaccinated_nonili{$country}{$year}{$week})) {
	    $unvaccinated_nonili{$country}{$year}{$week} = 0;
	}
    } else {
	if (!(exists $vaccinated_ili{$year}{$week})) {
	    $vaccinated_ili{$year}{$week} = 0;
	}
	if (!(exists $vaccinated_nonili{$year}{$week})) {
	    $vaccinated_nonili{$year}{$week} = 0;
	}
	if (!(exists $unvaccinated_ili{$year}{$week})) {
	    $unvaccinated_ili{$year}{$week} = 0;
	}
	if (!(exists $unvaccinated_nonili{$year}{$week})) {
	    $unvaccinated_nonili{$year}{$week} = 0;
	}
    }

    # see if we're an unvaccinated group
    # (which should be followed by a matching vaccinated group)
    if ($data[$vaccinated_index] == 0) {
	my @unvaccinated = @data;

	if (scalar (@nextdata) > $vaccinated_index) {
	    my $matching_group = 0;
	    if ($nextdata[$vaccinated_index] == 1) {
		$matching_group = 1;
		for (my $i = 0; $i < $vaccinated_index; $i++) {
		    if (!("$nextdata[$i]" eq "$unvaccinated[$i]")) {
			$matching_group = 0;
		    }
		}
	    }
	    if ($matching_group) {
		my @vaccinated = @nextdata;
		my $vaccinated_total =
		    $vaccinated[$ili_index] + $vaccinated[$nonili_index];
		my $unvaccinated_total =
		    $unvaccinated[$ili_index] + $unvaccinated[$nonili_index];
		my $smaller_total = min($vaccinated_total,
					$unvaccinated_total);
		if ($vaccinated_total > 0 && $unvaccinated_total > 0) {
		    if ($countries) {
			my $country = $vaccinated[$country_index];
			$unvaccinated_ili{$country}{$year}{$week} +=
			    $unvaccinated[$ili_index] *
				$smaller_total / $unvaccinated_total;
			$unvaccinated_nonili{$country}{$year}{$week} +=
			    $unvaccinated[$nonili_index] *
				$smaller_total / $unvaccinated_total;
			$vaccinated_ili{$country}{$year}{$week} +=
			    $vaccinated[$ili_index] *
				$smaller_total / $vaccinated_total;
			$vaccinated_nonili{$country}{$year}{$week} +=
			    $vaccinated[$nonili_index] *
				$smaller_total / $vaccinated_total;
		    } else {
			$unvaccinated_ili{$year}{$week} +=
			    $unvaccinated[$ili_index] *
				$smaller_total / $unvaccinated_total;
			$unvaccinated_nonili{$year}{$week} +=
			    $unvaccinated[$nonili_index] *
				$smaller_total / $unvaccinated_total;
			$vaccinated_ili{$year}{$week} +=
			    $vaccinated[$ili_index] *
				$smaller_total / $vaccinated_total;
			$vaccinated_nonili{$year}{$week} +=
			    $vaccinated[$nonili_index] *
				$smaller_total / $vaccinated_total;
		    }
		}
		my $line = <STDIN>;
		if ($line) {
		    chomp $line;
		    @nextdata = split /,/, $line;
		}
	    }
	}
    }
}

my @categories;
my @vaccinated_data;
my @unvaccinated_data;
if ($countries) {
    foreach my $country (sort keys %vaccinated_ili) {
	foreach my $year (sort keys %{ $vaccinated_ili{$country} }) {
	    foreach my $week (sort {$a <=> $b} keys %{ $vaccinated_ili{$country}{$year} }) {
		if ($vaccinated_ili{$country}{$year}{$week} +
			$vaccinated_nonili{$country}{$year}{$week} > 0 &&
			    $unvaccinated_ili{$country}{$year}{$week} +
				$unvaccinated_nonili{$country}{$year}{$week} >
				    0) {
		    push @categories, "$country,$year,$week";
		    push @vaccinated_data,
			sprintf("%.1f", ($vaccinated_ili{$country}{$year}{$week} * 100 /
					     ($vaccinated_ili{$country}{$year}{$week} +
						  $vaccinated_nonili{$country}{$year}{$week}
						      + .0)));
		    push @unvaccinated_data,
			sprintf("%.1f", ($unvaccinated_ili{$country}{$year}{$week} * 100 /
					     ($unvaccinated_ili{$country}{$year}{$week} +
						  $unvaccinated_nonili{$country}{$year}{$week}
						      + .0)));
		}
	    }
	}
    }
} else {
    foreach my $year (sort keys %vaccinated_ili) {
	foreach my $week (sort {$a <=> $b} keys %{ $vaccinated_ili{$year} }) {
	    if ($vaccinated_ili{$year}{$week} +
		    $vaccinated_nonili{$year}{$week} > 0 &&
			$unvaccinated_ili{$year}{$week} +
			    $unvaccinated_nonili{$year}{$week} >
				0) {
		if ($motionchart) {
		    push @categories, "'$week/$year'";
		} else {
		    push @categories, "$year,$week";
		}
		push @vaccinated_data,
		sprintf("%.1f", ($vaccinated_ili{$year}{$week} * 100 /
				     ($vaccinated_ili{$year}{$week} +
					  $vaccinated_nonili{$year}{$week} + .0)));
		push @unvaccinated_data,
		    sprintf("%.1f", ($unvaccinated_ili{$year}{$week} * 100 /
					 ($unvaccinated_ili{$year}{$week} +
					      $unvaccinated_nonili{$year}{$week} + .0)));
	    }
	}
    }
}

if ($motionchart) {
    # exclude first week
    shift(@categories); 
    shift(@vaccinated_data); 
    shift(@unvaccinated_data); 
    print "<html>\n";
    print "  <head>\n";
    print "    <script type=\"text/javascript\" ".
	"src=\"http://ajax.googleapis.com/ajax/libs/jquery/1.6.1/".
	    "jquery.min.js\"></script>\n";
    print "    <script type=\"text/javascript\" ".
	"src=\"/media/highcharts/highcharts.js\"></script>\n";
    print "    <script type=\"text/javascript\">\n";
    print "            var chart;\n";
    print "            \$(document).ready(function() {\n";
    print "                    chart = new Highcharts.Chart({\n";
    print "                            chart: {\n";
    print "                                    renderTo: 'container',\n";
    print "                                    defaultSeriesType: 'line',\n";
    print "                                    marginRight: 0,\n";
    print "                                    marginBottom: 70\n";
    print "                            },\n";
    print "                            title: {\n";
    print "                                    text: 'Incidence in vaccinated/unvaccinated groups',\n";
    print "                                    x: -20 //center\n";
    print "                            },\n";
    print "                            xAxis: {\n";
    print "                                    categories: [".join(',', @categories)."],\n";
    print "                                    labels: {\n";
    print "                                            rotation: -45,\n";
    print "                                            align: 'right'\n";
    print "                                    }\n";
    print "                            },\n";
    print "                            yAxis: {\n";
    print "                                    title: {\n";
    print "                                            text: 'Incidence (in %)'\n";
    print "                                    },\n";
    print "                                    plotLines: [{\n";
    print "                                            value: 0,\n";
    print "                                            width: 1,\n";
    print "                                            color: '#808080'\n";
    print "                                    }]\n";
    print "                            },\n";
    print "                            tooltip: {\n";
    print "                                    formatter: function() {\n";
    print "                                    return '<b>'+ this.series.name +'</b><br/>'+\n";
    print "                                                    'Incidence in week ' + this.x +': '+ this.y + '%';\n";
    print "                                    }\n";
    print "                            },\n";
    print "                            legend: {\n";
    print "                                    layout: 'vertical',\n";
    print "                                    align: 'right',\n";
    print "                                    verticalAlign: 'top',\n";
    print "                                    x: -10,\n";
    print "                                    y: 100,\n";
    print "                                    borderWidth: 0,\n";
    print "                                    enabled: false\n";
    print "                            },\n";
    print "                            series: [{\n";
    print "                                    name: 'Vaccinated',\n";
    print "                                    data: [".join(",", @vaccinated_data)."]\n";
    print "                            }, {\n";
    print "                                    name: 'Unvaccinated',\n";
    print "                                    data: [".join(",", @unvaccinated_data)."]\n";
    print "                            }]\n";
    print "                                });\n";
    print "                        });\n";
    print "    </script>\n";
    print "  </head>\n";
    print "  <body>\n";
    print "    <div id=\"container\" style=\"width: 550px; height: 300px; margin: 0 auto\"></div>\n";
    print "  </body>\n";
    print "</html>\n";
} else {
    if ($countries) {
	print "country,";
    }
    print "year,week,variable,value\n";
    for (my $i = 0; $i < (scalar @categories); $i++) {
	print "$categories[$i],vaccinated,$vaccinated_data[$i]\n";
	print "$categories[$i],unvaccinated,$unvaccinated_data[$i]\n";
    }
}
