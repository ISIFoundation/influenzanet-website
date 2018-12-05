(function($) {
    // IE fixes.

    if (!(Array.indexOf)) {
        Array.prototype.indexOf = function(obj) {
            for(var i=0; i<this.length; i++){
                if (this[i] == obj)
                    return i;
            }
            return -1;
        }
    }
    if (!('map' in Array.prototype)) {
        Array.prototype.map= function(mapper, that /*opt*/) {
            var other= new Array(this.length);
            for (var i= 0, n= this.length; i<n; i++)
                if (i in this)
                    other[i]= mapper.call(that, this[i], i, this);
            return other;
        };
    }

    // MODULE: wok.pollster

    window.wok = window.wok || {
        version: '1.0',
        error: function(msg) { alert("wok error: " + msg); }
    };

    window.wok.pollster = {
        options: {
            // UI part selectors.
            canvasSelector: "#pollster-canvas",
            propertiesSelector: "#pollster-properties",
            templateClass: "survey",
            questionClass: "question"
        }
    };

	function debug_rule(rule, target) {
		if(window.wok.debug_rule) {
			window.wok.debug_rule(rule, target);
		} else {
			console.log(rule);
		}
	}

    // POLLSTER SURVEY

    function PollsterRuntime(context, options) {
        context = context || document;
        options = $.extend({}, window.wok.pollster.options, options);

        var self = this;
        var $survey = $('.'+options.templateClass, context);
        var questionSelector = '.'+options.questionClass;

		this.debug = options.debug || false;

		this.setDebug = function(isDebug) {
			this.debug = isDebug;
		}

        // Useful methods.

        function get_homologous_rules(rule, rules) {
            var filtered = [];
            for (var i=0 ; i < rules.length ; i++) {
                var hr = rules[i];
                if (rule.objectSignature === hr.objectSignature && rule.name === hr.name)
                    filtered.push(hr);
            }
            return filtered;
        }

        // Fill types and rules from generated Javascript code.

        var last_participation_data = {};
        var data_types = {}, open_option_data_types = {}, derived_values = {};
        var rules_by_question = {}, rules_by_object = {};

        if (window.pollster_last_participation_data)
            last_participation_data = pollster_last_participation_data();
        if (window.pollster_fill_data_types)
            pollster_fill_data_types(data_types);
        if (window.pollster_fill_open_option_data_types)
            pollster_fill_open_option_data_types(open_option_data_types);
        if (window.pollster_fill_rules)
            pollster_fill_rules(rules_by_question);
        if (window.pollster_fill_derived_values)
            pollster_fill_derived_values(derived_values);

        // Fill the "by object" and "state" rule dictionaries.

        for (var q in rules_by_question) {
            // Create a list of all options for current question.

            var not_exclusive_options = [];
            $("#question-"+q+" li").each(function() {
                not_exclusive_options.push(parseInt(($(this).attr("id") || '').replace("option-","")));
            });

            for (var i=0 ; i < rules_by_question[q].length ; i++) {
                var rule = rules_by_question[q][i];
                if (rule.objectSignature !== null) {
                    var target = rules_by_object[rule.objectSignature];
                    if (!target) {
                        target = rules_by_object[rule.objectSignature] = {
                            state: { visibility: [0,0] },
                            rules: []
                        };
                    }
                    target.rules.push(rule);
                }

                // Set the initial active flag for the rule to false.
                rule.active = false;

                // If this is an ExclusiveRule instance remove subject options from the
                // list if not exclusive options; used later to generate an extra ExclusiveRule.

                if (rule.name == "ExclusiveRule") {
                    for (var j=0 ; j < rule.subjectOptions.length ; j++) {
                        var index = not_exclusive_options.indexOf(rule.subjectOptions[j]);
                        if (index >= 0)
                            not_exclusive_options.splice(index, 1);
                    }
                }
            }

            // Create one ExclusiveRule instance for each option that is not already
            // subject of an ExclusiveRule.

            rules_by_question[q].push(new window.wok.pollster.rules.Exclusive(q, not_exclusive_options, {}));
        }

        // Fill timestamp of last last participation data.

        $survey.find('.open-option-data').attr('disabled', true);
        if (last_participation_data && last_participation_data.timestamp)
            $('.question-builtin [name=timestamp]').val(last_participation_data.timestamp);

        // Bind data types to question elements

        $.each(data_types, function(question, data_type) {
            var $field = $('#question-'+question+'-field');
            data_type.bind($field);
        });

        $.each(open_option_data_types, function(question, option_data_types) {
            $.each(option_data_types, function(option, data_type) {
                var $field = $('#option-'+option+'-field-open');
                data_type.bind($field);
            });
        });

        // Event handlers.

        window.wok.pollster._eh_args = [];
        window.wok.pollster._eh = function() {
            var args = window.wok.pollster._eh_args.pop();
            if (!args) return;

            var evt = args[0];
            var extra = args[1];

            var $input = $(evt.target);
            var $question = $(evt.target).closest(questionSelector);
            var $option = $input.closest("li");

            if (!$question.length)
                return true;

            // Some checks are disabled on synthetized 'change' event.
            var synthetic = extra && extra.synthetic;
            var qid = parseInt($question.attr("id").replace("question-",""));
            var oid = null;
            if ($option.length)
                oid = parseInt($option.attr("id").replace("option-",""));

            // If the input is for the open data of an option apply datatype
            // checks and exit
            if ($input.hasClass('open-option-data')) {
                var data_type = open_option_data_types[qid][oid];
                if (data_type) {
                    var valid = data_type.check($input);
                    var empty = $input.val() == "";
                    var error = !valid || ($question.is('.mandatory') && empty);
                    if (!synthetic)
                        $question.toggleClass("error", error);
                }
                return true;
            }

            // If the INPUT is a checkbox or radio button with open data correctly
            // set the state of the INPUT depending on the checked state of the option.

            if ($input.is(":radio,:checkbox")) {
                $question.find('.open-option-data').attr('disabled', function() {
                    return !$(this).closest('li').find(":radio,:checkbox").is(':checked');
                });
            }

            // Else, if the INPUT is of type text execute the type checks.

            else {
                var data_type = data_types[qid];
                if (data_type) {
                    var valid = data_type.check($input);
                    var empty = $input.val() == "";
                    var error = !valid || ($question.is('.mandatory') && empty);
                    if (!synthetic)
                        $question.toggleClass("error", error);
                }
            }

            // Set the active flag on all rules for this event.

            var rules = rules_by_question[qid] || [];
            var rules_active = [];
            for (var i=0 ; i < rules.length ; i++) {
                var rule = rules[i];
                if (!rule.isFuture && rule.activate($survey, $question, evt))
                    rules_active.push(rule);
            }

            // For every active rule check "required" and "sufficient" conditions
            // for every rule with the same target object and type.

            for (var i=0 ; i < rules_active.length ; i++) {
                var rule = rules_active[i];
                var target = null, hrs = [];
                if (rule.objectSignature !== null) {
                    target = rules_by_object[rule.objectSignature];
                    hrs = get_homologous_rules(rule, target.rules);
                }

                // If the current rule was switched to active we just apply it if
                // sufficient, but if necessary we need to make sure all other
                // necessary rules are active too.

                if (rule.active) {
                    var apply = true;
                    if (!rule.isSufficient) {
                        for (var j=0 ; j < hrs.length ; j++) {
                            if (!hrs[j].isSufficient && !hrs[j].active)
                                apply = false;
                        }
                    }
                    if (apply) {
						rule.apply($survey, target);
						if(self.debug) {
							debug_rule(rule, target);
						}
					}
                }

                // If the current rule was switched to inactive we do as above
                // but the logic is inverted.

                else {
                    var apply = true;
                    if (rule.isSufficient) {
                        for (var j=0 ; j < hrs.length ; j++) {
                            if (hrs[j].isSufficient && hrs[j].active)
                                apply = false;
                        }
                    }
                    if (apply) {
						rule.apply($survey, target);
						if(self.debug) {
							debug_rule(rule, target);
						}
					}
                }
            }

            // Propagate changes to derived options.

            if ($input.is(':not(.derived)')) {
                var val = $input.val();
                var derived = derived_values[qid] || [];
                for (var i=0 ; i < derived.length ; i++) {
                    var $derived_input = $question.find('#option-'+derived[i].option).find(':input');
                    var match = Boolean(derived[i].match(val));
                    var checked = $derived_input.is(':checked');
                    if (match != checked) {
                        $derived_input.attr('checked', match).trigger('change', { synthetic: true });
                    }
                }
            }
        };

        $survey.find("input,select").change(function(evt, extra) {
            if (evt.target.nodeName !== "INPUT" && evt.target.nodeName !== "SELECT")
                return;
            window.wok.pollster._eh_args.push([evt, extra]);
            //setTimeout("window.wok.pollster._eh()", 1);
            window.wok.pollster._eh();
        });

        // Initialize all rules.

        jQuery.each(rules_by_question, function(i, by_question) {
            jQuery.each(by_question, function(i, rule) {
                rule.init($survey, last_participation_data);
            });
        });

        // Invoke future rules just once.

        for (var signature in rules_by_object) {
            var target = rules_by_object[signature];
            var required_fail = {};
            var sufficient_ok = {};
            for (var i=0 ; i < target.rules.length ; i++) {
                var rule = target.rules[i];
                if (rule.isFuture) {
                    if (rule.isSufficient) {
                        var ok = sufficient_ok[rule.name] || [false, null];
                        if (!ok[0] && rule.activate($survey, $survey.find("#question-"+rule.subjectQuestion), null)) {
                            sufficient_ok[rule.name] = [true, rule];
                        }
                    }
                    else {
                        var fail = required_fail[rule.name] || [false, null];
                        if (!fail[0] && rule.activate($survey, $survey.find("#question-"+rule.subjectQuestion), null)) {
                            required_fail[rule.name] = [false, rule];
                        }
                        else {
                            required_fail[rule.name] = [true, null];
                        }
                    }
                }
            }

            for (var k in sufficient_ok) {
                if (sufficient_ok[k][0] === true) {
					var r = sufficient_ok[k][1];
					r.apply($survey, target);
					if(this.debug) {
						debug_rule(r, target);
					}
				}
            }

            for (var k in required_fail) {
                if (required_fail[k][0] === false) {
					var r = required_fail[k][1];
					r.apply($survey, target);
					if(this.debug) {
						debug_rule(r, target);
					}
				}
            }

        }
		if(this.debug) {
			console.log('Future rules done');
		}

        // Ensure that the initial status is consistent with rules and whatnot.

        $survey.find(":input").trigger('change', { synthetic: true });

        // Setup info icons.

        $("ul.choices li").each(function() {
            var $li = $(this);
            var txt = $li.attr("title");
            if (txt) {
                var $tip = $('<div class="tip">'+txt+'</div>');
                var $img = $('<img src="/media/pollster/css/im/information.png"/>').hover(
                    function(evt) { $tip.fadeIn(); },
                    function(evt) { $tip.fadeOut(); }
                );
                $li.removeAttr("title").append($img);
                var pos = $li.offset();
                $tip.hide().css("position", "absolute").appendTo("body")
                    .offset({top: pos.top - $tip.outerHeight(), left: pos.left});
            }
        });
    }

    // MODULE FUNCTIONS

    window.wok.pollster.createPollsterRuntime = function(context, options) {
        return new PollsterRuntime(context, options);
    };

})(jQuery);

