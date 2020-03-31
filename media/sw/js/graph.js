function calc_user_group(profile, age_group) {
	if(!age_group) {
		age_group = 20;
	}
	if(!$.isPlainObject(profile) ) {
		return false;
	}
	var birth = profile.date_birth;
	if( !birth ) {
		return false;
	}
	birth = birth.split('-');
	var date = new Date();
	date.setFullYear(parseInt(birth[0]));
	date.setMonth(parseInt(birth[1])-1);
	var now = new Date();
	var age = now - date;
	if(age < 0) {
		return false;
	} else {
		age = Math.floor(age / (1000*60*60*24*365));
		group = Math.floor(age / age_group);
	}
	if(!profile.gender) {
		return false;
	}
	var upper_age = ((group + 1) * age_group) - 1;
	var lower_age = group * age_group;
	if(upper_age > 120) {
		upper_age = 120;
	}
	var gender_label = i18n_labels[ profile.gender];
	var label = lower_age + ' - ' + upper_age + ' ' + i18n_labels['years']+' / ' + gender_label;
	return {'id': profile.gender + '_' + group, 'label': label};
}


function prepare_data(data, column, my_group, translation) {
	var values = [],
	labels = [], // Bar labels
	colors = [], // Bar colors
	my_group_idx, // index of the group the user belongs to
	vv, i, label,
	units;
	i = 0;
	console.log(data);
	if(!data) {
		return false;
	}
	my_group_idx = -1;
	vv = data[column];
	if(column == 'prop') {
		units = '%';
	} else {
		units = '';
	}
	for(var n in vv) {
		values.push(vv[n]);
		if(translation) {
			label = translation[n];
		} else {
			label = n;
		}
		labels.push(label);
		if( n == my_group ) {
		 	my_group_idx = i;
			colors.push(app_config.color2);
		} else {
			colors.push(app_config.color1);
		}
		++i;
	}
	return {
		values: values,
		labels: labels,
		colors: colors,
		units: units,
		my_group: my_group_idx
	};
}

function create_labels(paper, barchart, horiz, data, chart_margin, label_margin, bar_label, show_avatar) {
	var set = paper.set(),
		covers = barchart.covers,
		bars = barchart.bars,
		n = covers.length;

	for(var i = 0; i < n; ++i) {
		// Left label
		var
			bin = covers[i].getBBox(), // bin bounds
			bb, base,
			x, y;

		if(horiz) {
			x = 0;
			y = bin.y + (bin.height / 2);
		} else {
			x = bin.x + (bin.width / 2);
			y = bin.y + bin.height - label_margin;
		}
		if(bar_label) {
			label = paper.text(x, y, data.labels[i]);
			w =  label.getBBox().width;
			if(horiz) {
				label.attr('x', chart_margin - w - label_margin )
			}
			set.push(label);
		}

		// Value label on the right of the bar
		bb = bars[i].getBBox();
		if(horiz) {
			if(bb.width == 0) {
				x = bin.x + 5;
			} else {
				x = bb.x + bb.width + 5;
			}
		} else {
			if(bb.height == 0) {
				y = bin.height - label_margin;
			} else {
				y = bb.y - label_margin;
			}
		}
		var text = data.values[i] + data.units;
		label = paper.text(x, y, text );
		set.push(label);

		if( show_avatar && i == data.my_group ) {
			bb = label.getBBox();
			//label = paper.text(bin.x + bin.width/2, bin.y + bin.height/2, "Vous");
			paper.image(user_avatar, x + bb.width + 4, y - 16, 32, 32);
		}
	}
	set.attr({'text-anchor': ((horiz) ? 'start' : 'middle')});
}


function syndrom_chart(container, json, health_status, last_health_status) {
	var
	margin_x = 160,
	label_margin_x = 5, // Margin between bar & labels
	w, paper, // Rapheal canvas
	all_hbar, x, group_hbar, label_graph,
	all_data, group, group_data, graph_data;

	all_data = prepare_data(json.data.syndrom, 'prop', last_health_status, health_status);
	group = calc_user_group(user_profile, json.params.age_group);
	if(group) {
		var group_data = json.data.syndrom_group[group.id];
		group_data = prepare_data(group_data, 'prop', last_health_status, health_status);
        if(!group_data) {
			group = false;
		}
	}
	w = (group) ? 620 : 520;
	paper = Raphael(container, w, 240);
	all_hbar = paper.hbarchart(margin_x, 0, 150, 200, all_data.values, { 'colors':all_data.colors });
	create_labels(paper, all_hbar, true, all_data, margin_x, label_margin_x, true, (group ? false : true));

	paper.text(margin_x + 40, 220, i18n_labels['all_participants']);

	if(group) {
		var x = margin_x + 150 + 50;
		group_hbar = paper.hbarchart(x, 0, 150, 200, group_data.values, { 'colors':group_data.colors });
		create_labels(paper, group_hbar, true, group_data, x, label_margin_x, false, true);
		paper.text(x + 40, 220, group.label);
	}

}

var months = ['Jan','Fev','Mar','Avr','Mai','Jun','Jui','Aou','Sep','Oct','Nov','Dec'];

function StoryRaphael(history, users) {
	var min = Number.MAX_VALUE; // Min timestamp
	var max = 0;	// Max timestamp
	var max_user_len = 0; // max length of username

	// Rebuild history by user, and extract stats
	var hh = { };
	var n = history.length;
	for(var i = 0; i < n; ++i) {
	  var h = history[i],  u = h.gid, time = h.time;
	  if(typeof(hh[u]) == 'undefined') {
		hh[u] = [];
	  }
	  hh[u].push({time:time, status:h.syndrom});
	  min = (time < min) ? time : min;
	  max = (time > max) ? time : max;
	}
	this.history = hh;
	this.min_day = min;
	this.max_day = max;

	var i = 0;
	for(g in users) {
		var n = users[g].length;
		max_user_len = (n > max_user_len) ? n : max_user_len;
		++i;
	}
	this.nb_users = i;
	this.max_user_len = max_user_len;
	this.users = users;
}

$.extend(StoryRaphael.prototype, {
	options: {
		'cell_w': 33, // width of cell (date)
		'cell_h': 33, // height of cell (user)
		'em': 5, // Size of one character (to adjust user names width)
		'margin_left':5,
		'margin_bottom': 20 // Margin used to plot calendar date (date + month)
	},
	render: function(id, options) {

		options = options || {};

		$.extend(options, this.options);

		// Parameters
		var dh = options.cell_h, // Height by user
			dw = options.cell_w, // Width by day
			nb_users = this.nb_users,
			nb_days = Math.ceil((this.max_day - this.min_day) / 86400), // Nb of days;
			hh = this.history,
			user_width = this.max_user_len * options.em + options.margin_left,
			height = (nb_users) * dh + options.margin_bottom,
			width = (nb_days + 1) * dw  + (user_width), // Width date cells + users names
			paper, base_x;

		console.log(id, width, height);

		var paper = Raphael(id, width, height);

		var base_x = 0;
		// draw grid
		for(var i = 0; i <= nb_days; ++i) {

			// Draw date lines
			x = base_x + dw * i;
			var path = "M"+ x + ",0" + "L"+x+","+height;
			var p = paper.path(path);
			p.attr("stroke","#EEE");

			// Dates
			var d = new Date();
			d.setTime( (this.min_day + (i * 86400)) * 1000);
			var a = {"font-size":"9px", "fill":"#AAA", 'stroke':'none' };
			x = x + Math.round(dw/2);
			var t = paper.text(x, height - 15, d.getDate() );
			t.attr(a);
			var t = paper.text(x, height - 5, months[d.getMonth()] );
			t.attr(a);
		}

		// Draw user lines and status
		var attr_text = { "font-size": "10px", "text-anchor": "start" };
		var attr_line = { "stroke": "#CCC", "stroke-width": 1};
		var i = 0;
		for(gid in this.users) {
			var y = i * dh + Math.round(dh / 2);
			var u = this.users[gid];

			// User name
			var x = base_x + (nb_days + 1) * dw + 2;
			var t = paper.text(x, y, u);
			t.attr(attr_text);

			// User line
			var x = base_x;
			var l = (nb_days + 1) * dw;
			var p = paper.path("M" + (x) + "," + y + "L" + (x + l ) + "," + y);
			p.attr(attr_line);
			h = hh[gid]; // user history
			if(h) {
				// User history
				var n = h.length;
				for(var j = 0; j < n; ++j) {
					var r = h[j];
					var d = Math.floor((r.time - this.min_day)/ 86400);
					x = base_x + Math.round( d  * dw ); // center the circle
					var status = r.status;
					var diag = health_status[status];
					var img = paper.image('/media/syndrom/32/' + status + '.png', x, y - 16, 32, 32 );
					var date = new Date();
					date.setTime(r.time*1000);
					img.attr({'title': date.toLocaleDateString() + ' : ' + u + ', ' + diag});
				}
			}
			i = i + 1;
		}
		var e = $('#'+id);
		// Scroll to last date
		var w = e.attr('scrollWidth');
		if(typeof(w) != 'undefined') {
			e.scrollLeft(w);
		}
	}


});




