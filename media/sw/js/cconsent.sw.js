$(function() {
	var name = app_config.name;
	$.cc.run({
		target: '#cc-box',
		types: {
			'essential': {
				title: 'Cookies de ' + name,
				desc: 'Ces cookies sont nécessaires au fonctionnement de '+name+', il n\'est pas possible de les désactiver.',
				base: true
			},
			'social': {
				title: 'Réseaux sociaux',
				desc: 'Ces cookies permettent aux réseaux sociaux de proposer des services (j\'aime, partager)',
				base: false
			},
			'analytics': {
				title: 'Analyse d\'audience',
				desc: 'Ces cookies permettent de suivre votre activité sur le site et mesurer son audience. Nous utilisons Google Analytics',
				base: false
			}
		},
		settings: {
			ignoreDoNotTrack: false,
			version: 1,
			txtInfo: 'Ce site utilise des cookies provenant de sites tiers',
			txtPolicy: '<a href="/cookies-policy" id="cookie-policy" data-facebox-width="800" data-facebox-height="560">En savoir plus</a>',
			txtApprove: 'J\'accepte',
			txtDecline: 'Je refuse',
			txtShow: 'Voir le détails',
			txtTypes: 'Les types de cookies ci dessous sont utilisés par ce site. En cliquant sur le bouton "J\'accepte" seuls les types de cookies cochés seront activés. En cliquant sur "Je refuse", ils seront tous désactivés.',
			consent: function(types) {
				if($.inArray('social', types)) {
					start_socials();
				}
				if( $.inArray('analytics') ) {
					start_ga();
				}
			}
		}
	});
	$('#cookie-policy').click(init_facebox_rel);
});