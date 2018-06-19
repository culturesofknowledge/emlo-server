
var colours = [
	'#31ccf6', '#37b5d8', '#df65b0', '#dd1c77', '#980043' // default
];

(function() {
	var map, solr,
		placesData = [],
		popupHighlight = null;

	var heatmapType = "geojsonGrid",
		gridLayer, clusterLayer;

	var monica = true;

	if( monica ) {
		L.mapbox.accessToken = 'pk.eyJ1IjoibW9uaWNhbXMiLCJhIjoiNW4zbEtPRSJ9.9IfutzjZrHdm2ESZTmk8Sw';
		map = L.mapbox.map('map', 'monicams.jpf4hpo5');
	}
	else {
		map = L.map('map');
	}

	//map.setView([39.82, -98.58], 4); // America
	map.setView([0, 0], 2); // World

	if( !monica ) {
		L.tileLayer('http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
		}).addTo(map);
	}

	function onEachFeature(feature, layer) {
		//var count = feature.properties.count.toLocaleString();
		//layer.bindTooltip(count + " places").openTooltip();
		//layer.bindPopup(count);
	}

	var solrErrorHandler = function (jqXHR, textStatus, errorThrown) {
		// due to jsonp, no details are available
		jQuery('#errorMessage').text('Solr error, bad URL or RPT field name');
	};

	var solrSuccessHandler = function (data, textStatus, jqXHR) {
		/*console.log("solrSuccessHandler",data);

		var dataGrid = data.facet_counts.facet_heatmaps.geo_rpt[15];
		var dgColumns = data.facet_counts.facet_heatmaps.geo_rpt[3]*1;
		console.log(dataGrid);

		var empty = [];
		for(var dgc=0, z=dgColumns; dgc<z;dgc++){
			empty.push(0);
		}

		for( var dg=0,z=dataGrid.length;dg<z;dg++) {
			if(!dataGrid[dg]) {
				dataGrid[dg] = empty;
			}
		}
		console.log(dataGrid);*/

		var placeNames = [];
		placesData = [];
		for (var i = 0, iEnd = data.response.docs.length; i < iEnd; i++) {
			placesData.push(data.response.docs[i]);
			data.response.docs[i].reverseName = data.response.docs[i]["n"]
				.replace(/, /g,",")
				.split(',').reverse().join(", ");
		}

		//var nameSort = function(r,l) { return r.geonames_name.localeCompare(l.geonames_name); };
		var reverseNameSort = function (r, l) {
			return r.reverseName.replace(/\(/g,"").replace(/\)/g,"").replace(/\[/g,"").replace(/\]/g,"")
				.localeCompare(l.reverseName.replace(/\(/g,"").replace(/\)/g,"").replace(/\[/g,"").replace(/\]/g,""));
		};
		placesData.sort(reverseNameSort);

		for (i = 0, iEnd = placesData.length; i < iEnd; i++) {
			//placeNames.push( "<option value='" + i + "'>" + placesData[i].reverseName + "  [" + placesData[i]["g"] + "]</option>" );
			placeNames.push(['<option value="', i, '">', placesData[i].reverseName, /*" - [", placesData[i]["g"], "]",*/ "</option>"].join(""));
		}

		jQuery('#placelist').html(placeNames.join(""));
		jQuery('#errorMessage').text('');
		jQuery('#responseTime').html('Solr response time: ' + solr.solrTime + ' ms');
		jQuery('#numDocs').html('Number of docs: ' + solr.docsCount.toLocaleString());
	};

	var renderCompleteHandler = function () {

		if (solr.renderTime) {
			$('#renderTime').html('Render time: ' + solr.renderTime + ' ms');
		}
	};

	var solrQueryCreate = function () {
		var filterVal = filter.value.trim();
		var field = "geonames_name:";
		var query;

		if( filterVal !== "" ) {
			var queryParts = [];
			var words = filterVal.split(" ");
			for (var i = 0, iEnd = words.length; i < iEnd; i++) {
				if (words[i] != "") {
					queryParts.push("(" + field + words[i] + " " + field + words[i] + "*)");
				}
			}

			query = queryParts.join(" AND ");
		}
		else {
			query = field + "*";
		}

		console.log(query);

		return query;
	};

	var tileClick = function(e) {
		var z = map.getZoom();
		map.setZoomAround(e.latlng,z+2);
	};

	jQuery('#placelist').on("change", function () {
		var index = jQuery('#placelist').val();
		var placeData = placesData[+index];

		var latlong = placeData["g"].split(",");
		if (popupHighlight === null) {
			popupHighlight = L.popup({
				autoPan: false
			})
			//.setLatLng([+latlong[0], +latlong[1]])
			//.openOn(map);
		}

		var title = placeData["n"].split(",").slice(0, -1).join(", ");
		if (title.trim() === "") {
			title = placeData["n"];
		}
		var url = "http://emlo.bodleian.ox.ac.uk/profile/location/" + placeData["i"].replace("uuid_", "");

		var content = "" +
			"<b>" + title + "</b><br/>" +
			((placeData["f"] !== 0)
				? "Sent from: " + placeData["f"] + " letters<br/>"
				: "") +
			((placeData["t"] !== 0)
				? "Sent to: " + placeData["t"] + " letters<br/>"
				: "") +
			((placeData["m"] !== 0)
				? "Mentioned: " + placeData["m"] + " letters<br/>"
				: "") +
			'<a href="' + url + '" target="_blank">Link to main record</a>';

		popupHighlight
			.setLatLng([+latlong[0], +latlong[1]])
			.setContent(content)
			.openOn(map);
	});

	jQuery("#filter").on( "keyup", function() {
		solr.refresh();
	});

	jQuery("#update").on( "click", function () {
		resetSolr();
	});

	jQuery("#clear").on( "click", function () {
		filter.value = "";
		solr.refresh();
	});

	/*jQuery("path.leaflet-clickable").on( "click", function () {
		console.log("Test clicking an area.")
	});*/

	function resetSolr() {
		"use strict";

		console.log("resetSolr");

		var colorMap = colours;
		var solrURL = window.location.origin + '/solr/locations';

		if (solr) {
			map.removeLayer(solr);
		}


		map.on('zoomend', function(e) {
			console.log(e);
			updateMap(e.target._zoom);
		});

		gridLayer = L.solrHeatmap(solrURL, {

				field: "geo_rpt",
				type: "geojsonGrid",

				colors: colorMap,
				maxSampleSize: 400,

				solrErrorHandler: solrErrorHandler,
				solrSuccessHandler: solrSuccessHandler,
				renderCompleteHandler: renderCompleteHandler,
				tileClick: tileClick,

				popupHighlight: true,
				showGlobalResults: false,
				fixedOpacity: 100,

				limitFields: [
					'g:geo',
					'n:geonames_name',
					'i:id',
					'f:ox_totalWorksSentFromPlace',
					't:ox_totalWorksSentToPlace',
					'm:ox_totalWorksMentioningPlace'
				],
				maxDocs: 10000,

				solrQueryCreate: solrQueryCreate
			})


		clusterLayer = L.solrHeatmap(solrURL, {

				field: "geo_rpt",
				type: "clusters",

				colors: colorMap,
				maxSampleSize: 400,

				solrErrorHandler: solrErrorHandler,
				solrSuccessHandler: solrSuccessHandler,
				renderCompleteHandler: null,//renderCompleteHandler

				popupHighlight: true,
				showGlobalResults: false,
				fixedOpacity: 100,

				limitFields: [
					'g:geo',
					'n:geonames_name',
					'i:id',
					'f:ox_totalWorksSentFromPlace',
					't:ox_totalWorksSentToPlace',
					'm:ox_totalWorksMentioningPlace'
				],
				maxDocs: 10000,

				solrQueryCreate: solrQueryCreate
			})

		updateMap();
	}

	function updateMap(zoom) {
		if(!zoom) {
			zoom = map.getZoom();
		}

		if( zoom < 6 ) {
			if( map.hasLayer(clusterLayer)) {
				map.removeLayer(clusterLayer);
			}
			solr = gridLayer.addTo(map);
		}
		else {
			if( map.hasLayer(gridLayer)) {
				map.removeLayer(gridLayer);
			}
			solr = clusterLayer.addTo(map);
		}
	}

	resetSolr();
})();

var coloursDiv = document.getElementById("colours");
//coloursDiv.appendChild(document.createTextNode("Key: "));

var spanLeast = document.createElement("span");
spanLeast.setAttribute("style", "margin-right:10px;vertical-align:bottom;display:inline-block;height:39px;");
spanLeast.appendChild(document.createTextNode("Least in view"));

var spanMost = document.createElement("span");
spanMost.setAttribute("style", "margin-left:10px;vertical-align:bottom;display:inline-block;height:39px;");
spanMost.appendChild(document.createTextNode("Most in view"));

coloursDiv.appendChild(spanLeast);
for( var colour=0, end=colours.length; colour<end;colour++ ) {
	var div = document.createElement("div");
	div.setAttribute("style", "display:inline-block;width:30px;height:39px;background-color:"+colours[colour]);
	coloursDiv.appendChild(div)
}
coloursDiv.appendChild(spanMost);
