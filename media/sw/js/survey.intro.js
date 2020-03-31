function startIntro(){
  var intro = introJs();
  var name = app_config.name;
	
  intro.setOptions({
  	tooltipClass: 'survey-intro',
	nextLabel: 'Suivant',
	prevLabel: 'Précédent',
	skipLabel: 'Fermer',
	doneLabel: 'Terminé',
    steps: [
      { 
        intro: "Bienvenu(e) sur l'espace participant de "+name +". Cette introduction va vous monter tout ce qu'il y a connaître sur cette page."
      },
      {
        element: '#people-table',
        intro: "Ce tableau vous permet de visualiser les participants de votre compte.",
		position: 'top'
      },
      {
        element: '#' + first_user +'-identity' ,
        intro: "Chaque participant est identifié par une image (avatar) et par un nom. <br/>Pour préserver votre vie privée<br/> utilisez de préférence un pseudo, surnom ou un mot (papa,...). Ces 'noms' et avatars vous aident à savoir de quel participant il s'agit si votre compte a plusieurs participants. Nous ne les utilisons pas pour traiter nos données.",
		position: 'right',
		tooltipClass: 'survey-intro large-intro'
      },
      {
        element: '#' + first_user +'-edit' ,
        intro: "Cliquer sur cet icone vous permet de modifier les caractéristiques d'un participant : changer son nom ou choisir un autre avatar pour ce participant (vous avez le choix entre une centaine d'avatars possibles !).",
		position: 'right'
      },
      {
        element: '#link-add-people' ,
        intro: "Vous pouvez rajouter un nouveau participant sur votre compte en cliquant sur ce lien. Votre compte peut ainsi regrouper les questionnaires de toute la famille.",
		position: 'top'
      },
      {
        element: '#button-delete' ,
        intro: "Vous pouvez également supprimer un participant de votre compte. Cochez la case à gauche du nom du participant puis cliquez sur ce bouton pour le supprimer.",
		position: 'top'
      },
     {
        element: '#' + first_user +'-intake'  ,
        intro: "Pour tout nouveau participant, la première chose à faire est de remplir le questionnaire préliminaire. C'est ce questionnaire qui permet de décrire un participant au début de la saison (si certains éléments changent il est possible de le modifier en cours de saison : par exemple si le participant a été vacciné contre la grippe)",
		position: 'top'
      },
     {
        element: '#' + first_user +'-cell-weekly'  ,
        intro: "Une fois le questionnaire préliminaire rempli, un bouton sera disponible dans cette case pour remplir le questionnaire <i>hebdomadaire</i> qui nous renseignera sur vos symptômes. L'idéal est de le remplir chaque semaine, <b>même si vous n'avez pas de symptôme</b>",
		position: 'top'
      },
     {
        element: '#button-healthy' ,
        intro: "Si plusieurs participants n'ont pas de symptôme, vous pouvez cocher la case à côté de leur nom puis cliquer sur ce bouton pour indiquer que tout va bien.",
		position: 'top'
      },
     {
        element: '#link-help-pages' ,
        intro: "Vous trouverez également un peu d'aide et d'explications sur ces pages.",
		position: 'left'
      },
     {
        element: '#link-dashboard' ,
        intro: "Vous retrouverez sur la page 'Vos résultats' un retour d'information sur les participants de votre compte. ",
		position: 'left'
      },
     {
        element: '#link-group' ,
        intro: "Gérez les participants de votre compte grace a ce lien.",
		position: 'left'
      },
     {
        element: '#header-user' ,
        intro: "Si vous avez une question ou que vous rencontrez un problème n'hésitez pas à utiliser la boite de commentaire.",
		position: 'bottom'
      }
	]
  });
  intro.start();
}