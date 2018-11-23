(function($) {
    window.wok.pollster.charts = {}

    function PollsterChart(container) {
        var self = this;

        self.$container = $(container);

        if (self.$container.length === 0)
            return wok.error("unable to get chart container element");

        var url = self.$container.attr('data-chart-url');
        if (url) {
            function getData(callback) {
                var params = {};
                var m = /gid=([a-z0-9-]+)/.exec(window.location.href);
                if (m && m[1])
                    params = {"gid":m[1]};
                $.getJSON(url, params, function(data, textStatus, jqXHR) {
                    callback(data);
                });
            }
        }

        function draw_map(url, containerId, center) {
            var jsonInput = $("#id_chartwrapper");
            var tileBase = url.replace(".json", "");

            getData(function(data) {

            	console.log('loaded', url, data);

            	var map = L.map(self.$container[0]).setView([data.bounds.lat, data.bounds.lng], data.bounds.z);

        		L.tileLayer('https://a.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
        		    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
        		    maxZoom: 18,
        		}).addTo(map);

        		var tile = L.tileLayer(tileBase + "/tile/{z}/{x}/{y}", {
        		    attribution: 'Map data GrippeNet.fr',
        		    maxZoom: 18,
        		}).addTo(map);

        		tile.on('click', function(event) {
        			console.log(event);
        		});

            });
        }

        function openEditor(jsonTargetId) {

        }

        // Public methods.

        $.extend(this, {
            openEditor: openEditor
        });

        if (self.$container.data("chart-type") === "google-charts")
            draw_chart(url, self.$container);
        else if (self.$container.data("chart-type") === "google-map")
            draw_map(url, self.$container, false);
        else if (self.$container.data("chart-type") === "google-map-centered")
            draw_map(url, self.$container, true);
    }

    window.wok.pollster.charts.init = function(callback) {
    	callback();
    };

    window.wok.pollster.charts.createCharts = function(selection) {
        $(selection).each(function() {
            var chart = new PollsterChart(this);
            $(this).data('pollster-chart', chart);
        });
    };

    window.wok.pollster.charts.activateChartEditor = function(selection) {
        $(selection).click(function(evt) {
            var id = $(this).attr('data-chart-id');
            var chart = $('#'+id).data('pollster-chart');
            var jsonTargetId = $(this).attr('data-json-target-id');
            chart.openEditor(jsonTargetId);
            return false;
        });
    };

})(jQuery);
