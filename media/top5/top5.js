$jq(document).ready(function() {
	$jq.ajaxSetup({
		beforeSend: function(xhr, settings) {
	         function getCookie(name) {
	             var cookieValue = null;
	             if (document.cookie && document.cookie != '') {
	                 var cookies = document.cookie.split(';');
	                 for (var i = 0; i < cookies.length; i++) {
	                     var cookie = jQuery.trim(cookies[i]);
	                     // Does this cookie string begin with the name we want?
	                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
	                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                         break;
	                     }
	                 }
	             }
	             return cookieValue;
	         }
	         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
	             // Only send the token to relative URLs i.e. locally.
	             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
	         }
	     }
	});
	 //inutile?
    $jq(".portlet")
    .addClass( "ui-widget ui-widget-content ui-helper-clearfix ui-corner-all" )
    .find( ".portlet-header" )
        .addClass( "ui-widget-header ui-corner-all" )
        .prepend( "<span class='ui-icon ui-icon-minusthick portlet-toggle'></span>");

    $jq(".portlet-toggle").on( "click", function() {
        var icon = $jq( this );
        console.log("test portlet toggle");
        icon.toggleClass( "ui-icon-minusthick ui-icon-plusthick" );
        icon.closest( ".portlet" ).find( ".portlet-content" ).toggle();
    });
    $jq("#sortable").sortable();
    // Sortable
    $jq("#accordion-resume").sortable({
        connectWith: "#accordion-resume",
        handle: ".portlet-header",
        cancel: ".portlet-toggle",
        placeholder: "portlet-placeholder ui-corner-all ui-state-highlight",
        update: function (event, ui) {},
    });

    $jq('#accordion-resume').on('sortupdate', function(event, ui) {
        var revues = $jq('.panel-dragable');
        var urank = 0;
        $jq.each(revues, function (i, rev) {
            urank = i + 1;
            var $rev = $jq(rev);
            var $serv = $rev.data('service');
            $rev.data('rank', $serv);
            $rev.find('#rank-' + $serv).html(urank);
            $jq('#hidden-rank-' + $serv).val(urank);
        });
     });

    $jq('.btn-toggle').click( function() {
    	var $this = $jq(this);
    	var $form = $($this.data('form'));
    	var $panel = $($this.data('panel'));
    	var $service =  $this.data('service');

		$jq.ajax({
			url: $form.attr('action'),
			data: {
	        	'service' : $service,
	        },
			type: $form.attr('method'),
	        dataType: 'json',
	        success : function (data){
	        		if(data.action =="Creation") {
	        			$panel.removeClass("panel-default");
	        			$panel.addClass("panel-warning");
	        		}
	        		if(data.action =="Error"){
	        			alert("Une erreur s'est produite, veuillez vous reconnecter et recommencer. \n\n "+
	        					"Si jamais l'erreur se reproduit, merci de contacter notre service informatique à l'adresse suivante : rs-dev@u707.jussieu.fr \n\n"+
	        					"Nous nous excusons pour ce désagrément et vous remercions de l'interêt que vous portez à notre étude.")
	        		}

	        },
	        error: function(data){

	        	console.log("error during creation of the rank")
	        }
        });
    });

	$jq('.pertinency-revue').click( function() {
		var error = 0 ;
		var $this = $jq(this);
		var $input_chbox = $($this.data('input'));

		var $form = $($this.data('form'));
		var $span = $($this.data('span'));
		var $panel = $($this.data('panel'));

		if ($this.hasClass('btn-warning')) {
			$span.text(" J\’ajoute à ma top 5");
			$input_chbox.attr("value", '0');
			$input_chbox.attr( "checked", false );
		}else{
			$span.text(" J\’enlève de ma top 5");
			$input_chbox.attr("value", '1');
			$input_chbox.attr( "checked", true );
		}
		$this.toggleClass('btn-warning btn-danger');
		$span.toggleClass('glyphicon-star glyphicon-star-empty');
		$panel.toggleClass('panel-danger panel-warning');

		var $collapse = $($this.data('collapse'));
		var $service = $this.data('service'); //service ou service.id? a modifier dans le html
		console.log($service);
		var $pertinency = $input_chbox.val();

		$jq.ajax({
			url: $form.attr('action'),
			data: {
	        	'service' : $service,
	        	'pertinency': $pertinency,
	        },
			type: $form.attr('method'),
	        dataType: 'json',
	        success : function (data){
	        		if (data.exists){
	        			nbRated = data.nbRated;
	        		}else{
	        			error = 1 ;
	        		}
	        },
	        error: function(data){
    			error = 1 ;

	        	console.log("error pertinency revue")
	        	console.log("data : "+Object.keys(data))
	        	console.log("status : "+data.status +' - '+ data.statusText)
	        }
        });
		if(error != 1){
			console.log(error)
			if($pertinency == 1 ){
				alert('Le service médical a bien été ajouté à votre liste.');
			}else{
				alert('Le service médical a bien été retiré de votre liste.');
			}
		}else{
			alert("Votre selection n'a pas été prise en compte. Veuillez actualiser la page et vous reconnecter s'il vous plait.");
		}

		$collapse.toggleClass('in');
	});
	$jq('#goto-rank').click(function(e) {
        if (nbRated != 5) {
            e.preventDefault();
            if(nbRated < 5){
            	nb = 5 - nbRated;
            	alert('Vous avez sélectionné '+nbRated+' service(s) médical(aux). Vous devez encore en sélectionner '+nb+' afin d\'accéder à votre classement.');
            }else{
            	nb = nbRated - 5;
            	alert('Vous avez sélectionné '+nbRated+' services médicaux. Vous devez en retirer '+nb+' afin d\'accéder à votre classement. Pour cela, cliquez sur le nom du service médical que vous souhaitez retirer puis tout en bas du résumé sur le bouton \"J\'enlève de ma Top 5\".');
            }
        }
    });
	$jq('#submit-rank').click(function(e) {
        e.preventDefault();
        var $this = $jq(this);
        if (confirm('Vous allez valider définitivement votre classement, confirmer ?')) {
        	if (confirm("Merci beaucoup d’avoir participé à cette étude « Top 5 » !\n\n" +
        			"Vous allez être redirigé vers un questionnaire complémentaire, qui nous permettra de mieux comprendre comment vous avez élaboré cette liste. Rassurez-vous, ce questionnaire est très court et ne vous prendra qu’une ou deux minutes de plus !\n\n" +
        			"Si vous avez plusieurs participants inscrits sur votre compte GrippeNet.fr, ne soyez pas surpris, la page sur laquelle vous allez arriver vous proposera la liste des participants de votre compte. Il vous suffira de cliquer sur votre nom.\n\n" +
        			"Encore un grand merci !\n\n\n")) {
        	//alert("Merci beaucoup d’avoir participé à cette étude « Top 5 » !\n\n " +
        	//		"Vous allez être redirigé vers un questionnaire complémentaire, qui nous permettra de mieux comprendre comment vous avez élaboré cette liste. Rassurez-vous, ce questionnaire est très court et ne vous prendra qu’une ou deux minutes de plus !\n\n" +
        	//		"Si vous avez plusieurs participants inscrits sur votre compte GrippeNet.fr, ne soyez pas surpris, la page sur laquelle vous allez arriver vous proposera la liste des participants de votre compte. Il vous suffira de cliquer sur votre nom.\n\n" +
        	//		"Encore un grand merci !\n\n\n");
            $this.unbind('click');
            $this.click();
        	}
        }
    });
	$jq('#save-rank').click(function(e) {
        var $this = $jq(this);
        alert('Vous avez sauvegardé votre classement temporaire, vous pourrez le retrouver lors de votre prochaine connexion.');
    });

	$jq('.btn-close').click(function(e) {
        var $this = $jq(this);
        var $collapse = $($this.data('collapse'));
        var $service = $this.data('service');
		$jq.ajax({
			url: action="/fr/top5/close/",
			data: {
	        	'service' : $service,
	        },
			type: "POST",
	        dataType: 'json',
	        success : function (data){
	        		if (data.close){
	        			console.log("Closing time saved")
	        		}
	        },
	        error: function(data){
	        	console.log("error during closing tab")
	        	console.log("data : "+Object.keys(data))
	        	console.log("status : "+data.status +' - '+ data.statusText)
	        }
        });
		$collapse.toggleClass('in');
    });


    $jq(".refbody").hide();

	$jq(".refnum").click(function(event) {
		$jq(this.nextSibling).toggle();
          event.stopPropagation();
        });

	$jq("body").click(function(event) {
		$jq(".refbody").hide();
        });

});
