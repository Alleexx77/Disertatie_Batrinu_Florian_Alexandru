// This is a Showcase. CAS Software AG does not offer any support regarding this code.
// interval function that is called onload
function interval() {
    smartdesign.connect().then(api => {
        window.addEventListener('resize', () => {
            resize(api);
		});
		createTree().then(() => window.requestAnimationFrame(() => resize(api)));
    })
}

// Create the Tree
async function createTree() {
	let node = await findParent();
	let visited = []
	await buildTreeConfig(node, undefined, chart_config, visited)
	new Treant(chart_config);
}

// Find parent and parents of these parents of the company the user is on
async function findParent(){
	let api = await getApi();
	let gguid = api.State.current.gguid;
	let nodeFound = false;
	let loopDetected = false;
	let loopArray = [];

	while (!nodeFound && !loopDetected){
		let query = ("SELECT GUID2 FROM TABLERELATION WHERE RELATIONNAME = 'L2UADRHIERARCHY' AND DIRECTION = 1 AND GUID1 = 0x" + gguid);
		let resp = await api.fetch('v6.0/query', {
			method: 'POST',
			body: JSON.stringify({query}),
			headers: {
				'Content-Type': 'application/json'
			}
		});
		if (!resp.ok) {
			let text = await resp.text();
			throw Error(resp.statusText + "<br>" + text);	
		}
		// Get response
		let json = await resp.json();
		// when response is empty (no parent found)
		if (Object.keys(json).length == 0){
			nodeFound = true;
		} else {
			// if guid is already contained in the array, an endless loop is detected
			if (loopArray.includes(json[0].rows[0].GUID2)){
				loopDetected = true;
			}else{
				gguid = json[0].rows[0].GUID2;
				loopArray.push(gguid);
			}
		}
	}
	return gguid;
}

// Build the chart_config file for the tree
async function buildTreeConfig(gguid, parent, chart_config, visited) {
	let childGguids = await getChildren(gguid)
	let activeNode = null 
	let compInfo = await getCompanyInformation(gguid);
	if (compInfo == "NoCompanyFound" || visited.includes(gguid)){
		return
	}
	if(parent) {
		activeNode = await createNode(parent, gguid)
	} else {
		activeNode = await createAnchor(gguid)
	}
	visited.push(gguid);
	chart_config.push(activeNode);
	let promises = childGguids.map(child => {
		return buildTreeConfig(child, activeNode, chart_config, visited)
	})
	return Promise.all(promises)
}

// Get the API from smartdesign. You don't need a rest-key because this file is loaded within the gW Web Client.
async function getApi() {
	if (!window.api) {
		window.api = await smartdesign.connect();
	}
	return window.api;
}

// Get all children of the current gguid
async function getChildren(gguid){
	let api = await getApi();
	let childrenArray = [];
	let query = ("SELECT GUID2 FROM TABLERELATION WHERE RELATIONNAME = 'L2UADRHIERARCHY' AND DIRECTION = 2 AND GUID1 = 0x" + gguid);
	
	let resp = await api.fetch('v6.0/query', {
		method: 'POST',
		body: JSON.stringify({query}),
		headers: {
			'Content-Type': 'application/json'
		}
	});
	if (!resp.ok) {
		let text = await resp.text();
		throw Error(resp.statusText + "<br>" + text);	
	}
	let json = await resp.json();
	//when response is empty, no more children found
	if (Object.keys(json).length == 0){
		return childrenArray;
	} else {
		for (let i = 0; i < json[0].rows.length; i++) {
			childrenArray.push(json[0].rows[i].GUID2);
		}
		return childrenArray;
	}
}
	
// get Company Name from GUID input. When the Address doesnt exist or is not a company , return "NoCompanyFound"
async function getCompanyInformation(guid){
	let api = await getApi();	
	let resp = await api.fetch("v6.0/type/address/" + guid + "?fields=COMPNAME,GWISCONTACT,GWISCOMPANY,TOWN1,COUNTRY1");
	if (resp.ok){
		let compInfo = await resp.json();
		if (compInfo.fields.GWISCONTACT == 0 && compInfo.fields.GWISCOMPANY == 1){

			let name = compInfo.fields.COMPNAME;
			let place = compInfo.fields.TOWN1;
			let country = await translate(compInfo.fields.COUNTRY1);

			if (name == undefined){
				name = '';
			}

			if (place == undefined){
				place = '';
			}

			if (country == undefined){
				country = '';
			}
			let response = [name,place,country];
			return response;
		} else {
			return "NoCompanyFound"
		}
	} else {
		return "NoCompanyFound"
	}
}

// create anchor object for chart_config
async function createAnchor(guid){
	let compInfo = await getCompanyInformation(guid); 
	let api = await getApi();
	let gguid = api.State.current.gguid;
	let hClass = 'white';
	if (guid == gguid){
		hClass = 'blue';
	}
	var anchor = {
        text: {
			name: compInfo[0],  
			place: compInfo[1],
			country: compInfo[2]         
        },
        HTMLclass: hClass,
		link: {
            href: 'javascript:navigateToGUID("' + guid + '");'
		}
	}
	return anchor;
}

// create Node Object for chart_config
async function createNode(parentObject, guid) {
	let api = await getApi();
	let gguid = api.State.current.gguid;
	let hClass = 'white';
	let compInfo = await getCompanyInformation(guid);
	if (guid == gguid){
		hClass = 'blue';
	}
	var object = {
        parent: parentObject,
        text:{
			name: compInfo[0],
			place: compInfo[1],
			country: compInfo[2]
			
        },
        HTMLclass: hClass,
		link: {
            href: 'javascript:navigateToGUID("' + guid + '");'
		}
    }
	return object;
}

// Call the navigate function from smartdesign API. Open in new Tab
async function navigateToGUID(guid) {
let api = await getApi()
.then (function(smartdesign) {
smartdesign.Navigation.navigateWithRecord('ADDRESS', guid).openOnNewTab();
});
}

//resize height of the webWidget in smartdesign as the table grows
function resize(api){
	let tree = document.getElementById("company-structure")
	api.requestResize(-1, tree.clientHeight + 10 );
}

// Default header from chart_config
var config = {
		callback : {onTreeLoaded :() => getApi().then(api =>resize(api))},
        container: "#company-structure",
		nodeAlign: "TOP",
		scrollbar: "None",
        
        connectors: {
            type: 'step'
        },
        node: {
            HTMLclass: 'nodeDesign'
        }
    }
	
// chart_config array
var chart_config = [
    config,
	];	
	
async function translate(Ccode){
	let countryList  = [ 
		{"name": "Afghanistan", "code": "AF"}, 
		{"name": "land Islands", "code": "AX"}, 
		{"name": "Albania", "code": "AL"}, 
		{"name": "Algeria", "code": "DZ"}, 
		{"name": "American Samoa", "code": "AS"}, 
		{"name": "AndorrA", "code": "AD"}, 
		{"name": "Angola", "code": "AO"}, 
		{"name": "Anguilla", "code": "AI"}, 
		{"name": "Antarctica", "code": "AQ"}, 
		{"name": "Antigua and Barbuda", "code": "AG"}, 
		{"name": "Argentina", "code": "AR"}, 
		{"name": "Armenia", "code": "AM"}, 
		{"name": "Aruba", "code": "AW"}, 
		{"name": "Australia", "code": "AU"}, 
		{"name": "Austria", "code": "AT"}, 
		{"name": "Azerbaijan", "code": "AZ"}, 
		{"name": "Bahamas", "code": "BS"}, 
		{"name": "Bahrain", "code": "BH"}, 
		{"name": "Bangladesh", "code": "BD"}, 
		{"name": "Barbados", "code": "BB"}, 
		{"name": "Belarus", "code": "BY"}, 
		{"name": "Belgium", "code": "BE"}, 
		{"name": "Belize", "code": "BZ"}, 
		{"name": "Benin", "code": "BJ"}, 
		{"name": "Bermuda", "code": "BM"}, 
		{"name": "Bhutan", "code": "BT"}, 
		{"name": "Bolivia", "code": "BO"}, 
		{"name": "Bosnia and Herzegovina", "code": "BA"}, 
		{"name": "Botswana", "code": "BW"}, 
		{"name": "Bouvet Island", "code": "BV"}, 
		{"name": "Brazil", "code": "BR"}, 
		{"name": "British Indian Ocean Territory", "code": "IO"}, 
		{"name": "Brunei Darussalam", "code": "BN"}, 
		{"name": "Bulgaria", "code": "BG"}, 
		{"name": "Burkina Faso", "code": "BF"}, 
		{"name": "Burundi", "code": "BI"}, 
		{"name": "Cambodia", "code": "KH"}, 
		{"name": "Cameroon", "code": "CM"}, 
		{"name": "Canada", "code": "CA"}, 
		{"name": "Cape Verde", "code": "CV"}, 
		{"name": "Cayman Islands", "code": "KY"}, 
		{"name": "Central African Republic", "code": "CF"}, 
		{"name": "Chad", "code": "TD"}, 
		{"name": "Chile", "code": "CL"}, 
		{"name": "China", "code": "CN"}, 
		{"name": "Christmas Island", "code": "CX"}, 
		{"name": "Cocos (Keeling) Islands", "code": "CC"}, 
		{"name": "Colombia", "code": "CO"}, 
		{"name": "Comoros", "code": "KM"}, 
		{"name": "Congo", "code": "CG"}, 
		{"name": "Congo, The Democratic Republic of the", "code": "CD"}, 
		{"name": "Cook Islands", "code": "CK"}, 
		{"name": "Costa Rica", "code": "CR"}, 
		{"name": "Cote DIvoire", "code": "CI"}, 
		{"name": "Croatia", "code": "HR"}, 
		{"name": "Cuba", "code": "CU"}, 
		{"name": "Cyprus", "code": "CY"}, 
		{"name": "Czech Republic", "code": "CZ"}, 
		{"name": "Denmark", "code": "DK"}, 
		{"name": "Djibouti", "code": "DJ"}, 
		{"name": "Dominica", "code": "DM"}, 
		{"name": "Dominican Republic", "code": "DO"}, 
		{"name": "Ecuador", "code": "EC"}, 
		{"name": "Egypt", "code": "EG"}, 
		{"name": "El Salvador", "code": "SV"}, 
		{"name": "Equatorial Guinea", "code": "GQ"}, 
		{"name": "Eritrea", "code": "ER"}, 
		{"name": "Estonia", "code": "EE"}, 
		{"name": "Ethiopia", "code": "ET"}, 
		{"name": "Falkland Islands (Malvinas)", "code": "FK"}, 
		{"name": "Faroe Islands", "code": "FO"}, 
		{"name": "Fiji", "code": "FJ"}, 
		{"name": "Finland", "code": "FI"}, 
		{"name": "France", "code": "FR"}, 
		{"name": "French Guiana", "code": "GF"}, 
		{"name": "French Polynesia", "code": "PF"}, 
		{"name": "French Southern Territories", "code": "TF"}, 
		{"name": "Gabon", "code": "GA"}, 
		{"name": "Gambia", "code": "GM"}, 
		{"name": "Georgia", "code": "GE"}, 
		{"name": "Germany", "code": "DE"}, 
		{"name": "Ghana", "code": "GH"}, 
		{"name": "Gibraltar", "code": "GI"}, 
		{"name": "Greece", "code": "GR"}, 
		{"name": "Greenland", "code": "GL"}, 
		{"name": "Grenada", "code": "GD"}, 
		{"name": "Guadeloupe", "code": "GP"}, 
		{"name": "Guam", "code": "GU"}, 
		{"name": "Guatemala", "code": "GT"}, 
		{"name": "Guernsey", "code": "GG"}, 
		{"name": "Guinea", "code": "GN"}, 
		{"name": "Guinea-Bissau", "code": "GW"}, 
		{"name": "Guyana", "code": "GY"}, 
		{"name": "Haiti", "code": "HT"}, 
		{"name": "Heard Island and Mcdonald Islands", "code": "HM"}, 
		{"name": "Holy See (Vatican City State)", "code": "VA"}, 
		{"name": "Honduras", "code": "HN"}, 
		{"name": "Hong Kong", "code": "HK"}, 
		{"name": "Hungary", "code": "HU"}, 
		{"name": "Iceland", "code": "IS"}, 
		{"name": "India", "code": "IN"}, 
		{"name": "Indonesia", "code": "ID"}, 
		{"name": "Iran, Islamic Republic Of", "code": "IR"}, 
		{"name": "Iraq", "code": "IQ"}, 
		{"name": "Ireland", "code": "IE"}, 
		{"name": "Isle of Man", "code": "IM"}, 
		{"name": "Israel", "code": "IL"}, 
		{"name": "Italy", "code": "IT"}, 
		{"name": "Jamaica", "code": "JM"}, 
		{"name": "Japan", "code": "JP"}, 
		{"name": "Jersey", "code": "JE"}, 
		{"name": "Jordan", "code": "JO"}, 
		{"name": "Kazakhstan", "code": "KZ"}, 
		{"name": "Kenya", "code": "KE"}, 
		{"name": "Kiribati", "code": "KI"}, 
		{"name": "Korea, Democratic Peoples Republic of", "code": "KP"}, 
		{"name": "Korea, Republic of", "code": "KR"}, 
		{"name": "Kuwait", "code": "KW"}, 
		{"name": "Kyrgyzstan", "code": "KG"}, 
		{"name": "Lao PeopleS Democratic Republic", "code": "LA"}, 
		{"name": "Latvia", "code": "LV"}, 
		{"name": "Lebanon", "code": "LB"}, 
		{"name": "Lesotho", "code": "LS"}, 
		{"name": "Liberia", "code": "LR"}, 
		{"name": "Libyan Arab Jamahiriya", "code": "LY"}, 
		{"name": "Liechtenstein", "code": "LI"}, 
		{"name": "Lithuania", "code": "LT"}, 
		{"name": "Luxembourg", "code": "LU"}, 
		{"name": "Macao", "code": "MO"}, 
		{"name": "Macedonia, The Former Yugoslav Republic of", "code": "MK"}, 
		{"name": "Madagascar", "code": "MG"}, 
		{"name": "Malawi", "code": "MW"}, 
		{"name": "Malaysia", "code": "MY"}, 
		{"name": "Maldives", "code": "MV"}, 
		{"name": "Mali", "code": "ML"}, 
		{"name": "Malta", "code": "MT"}, 
		{"name": "Marshall Islands", "code": "MH"}, 
		{"name": "Martinique", "code": "MQ"}, 
		{"name": "Mauritania", "code": "MR"}, 
		{"name": "Mauritius", "code": "MU"}, 
		{"name": "Mayotte", "code": "YT"}, 
		{"name": "Mexico", "code": "MX"}, 
		{"name": "Micronesia, Federated States of", "code": "FM"}, 
		{"name": "Moldova, Republic of", "code": "MD"}, 
		{"name": "Monaco", "code": "MC"}, 
		{"name": "Mongolia", "code": "MN"}, 
		{"name": "Montenegro", "code": "ME"},
		{"name": "Montserrat", "code": "MS"},
		{"name": "Morocco", "code": "MA"}, 
		{"name": "Mozambique", "code": "MZ"}, 
		{"name": "Myanmar", "code": "MM"}, 
		{"name": "Namibia", "code": "NA"}, 
		{"name": "Nauru", "code": "NR"}, 
		{"name": "Nepal", "code": "NP"}, 
		{"name": "Netherlands", "code": "NL"}, 
		{"name": "Netherlands Antilles", "code": "AN"}, 
		{"name": "New Caledonia", "code": "NC"}, 
		{"name": "New Zealand", "code": "NZ"}, 
		{"name": "Nicaragua", "code": "NI"}, 
		{"name": "Niger", "code": "NE"}, 
		{"name": "Nigeria", "code": "NG"}, 
		{"name": "Niue", "code": "NU"}, 
		{"name": "Norfolk Island", "code": "NF"}, 
		{"name": "Northern Mariana Islands", "code": "MP"}, 
		{"name": "Norway", "code": "NO"}, 
		{"name": "Oman", "code": "OM"}, 
		{"name": "Pakistan", "code": "PK"}, 
		{"name": "Palau", "code": "PW"}, 
		{"name": "Palestinian Territory, Occupied", "code": "PS"}, 
		{"name": "Panama", "code": "PA"}, 
		{"name": "Papua New Guinea", "code": "PG"}, 
		{"name": "Paraguay", "code": "PY"}, 
		{"name": "Peru", "code": "PE"}, 
		{"name": "Philippines", "code": "PH"}, 
		{"name": "Pitcairn", "code": "PN"}, 
		{"name": "Poland", "code": "PL"}, 
		{"name": "Portugal", "code": "PT"}, 
		{"name": "Puerto Rico", "code": "PR"}, 
		{"name": "Qatar", "code": "QA"}, 
		{"name": "Reunion", "code": "RE"}, 
		{"name": "Romania", "code": "RO"}, 
		{"name": "Russian Federation", "code": "RU"}, 
		{"name": "RWANDA", "code": "RW"}, 
		{"name": "Saint Helena", "code": "SH"}, 
		{"name": "Saint Kitts and Nevis", "code": "KN"}, 
		{"name": "Saint Lucia", "code": "LC"}, 
		{"name": "Saint Pierre and Miquelon", "code": "PM"}, 
		{"name": "Saint Vincent and the Grenadines", "code": "VC"}, 
		{"name": "Samoa", "code": "WS"}, 
		{"name": "San Marino", "code": "SM"}, 
		{"name": "Sao Tome and Principe", "code": "ST"}, 
		{"name": "Saudi Arabia", "code": "SA"}, 
		{"name": "Senegal", "code": "SN"}, 
		{"name": "Serbia", "code": "RS"}, 
		{"name": "Seychelles", "code": "SC"}, 
		{"name": "Sierra Leone", "code": "SL"}, 
		{"name": "Singapore", "code": "SG"}, 
		{"name": "Slovakia", "code": "SK"}, 
		{"name": "Slovenia", "code": "SI"}, 
		{"name": "Solomon Islands", "code": "SB"}, 
		{"name": "Somalia", "code": "SO"}, 
		{"name": "South Africa", "code": "ZA"}, 
		{"name": "South Georgia and the South Sandwich Islands", "code": "GS"}, 
		{"name": "Spain", "code": "ES"}, 
		{"name": "Sri Lanka", "code": "LK"}, 
		{"name": "Sudan", "code": "SD"}, 
		{"name": "Suriname", "code": "SR"}, 
		{"name": "Svalbard and Jan Mayen", "code": "SJ"}, 
		{"name": "Swaziland", "code": "SZ"}, 
		{"name": "Sweden", "code": "SE"}, 
		{"name": "Switzerland", "code": "CH"}, 
		{"name": "Syrian Arab Republic", "code": "SY"}, 
		{"name": "Taiwan, Province of China", "code": "TW"}, 
		{"name": "Tajikistan", "code": "TJ"}, 
		{"name": "Tanzania, United Republic of", "code": "TZ"}, 
		{"name": "Thailand", "code": "TH"}, 
		{"name": "Timor-Leste", "code": "TL"}, 
		{"name": "Togo", "code": "TG"}, 
		{"name": "Tokelau", "code": "TK"}, 
		{"name": "Tonga", "code": "TO"}, 
		{"name": "Trinidad and Tobago", "code": "TT"}, 
		{"name": "Tunisia", "code": "TN"}, 
		{"name": "Turkey", "code": "TR"}, 
		{"name": "Turkmenistan", "code": "TM"}, 
		{"name": "Turks and Caicos Islands", "code": "TC"}, 
		{"name": "Tuvalu", "code": "TV"}, 
		{"name": "Uganda", "code": "UG"}, 
		{"name": "Ukraine", "code": "UA"}, 
		{"name": "United Arab Emirates", "code": "AE"}, 
		{"name": "United Kingdom", "code": "GB"}, 
		{"name": "United States", "code": "US"}, 
		{"name": "United States Minor Outlying Islands", "code": "UM"}, 
		{"name": "Uruguay", "code": "UY"}, 
		{"name": "Uzbekistan", "code": "UZ"}, 
		{"name": "Vanuatu", "code": "VU"}, 
		{"name": "Venezuela", "code": "VE"}, 
		{"name": "Viet Nam", "code": "VN"}, 
		{"name": "Virgin Islands, British", "code": "VG"}, 
		{"name": "Virgin Islands, U.S.", "code": "VI"}, 
		{"name": "Wallis and Futuna", "code": "WF"}, 
		{"name": "Western Sahara", "code": "EH"}, 
		{"name": "Yemen", "code": "YE"}, 
		{"name": "Zambia", "code": "ZM"}, 
		{"name": "Zimbabwe", "code": "ZW"} 
		]
		let result = countryList.filter(({name, code})=> code == Ccode).map(({name,code}) => name)
		return result[0];
}
	
	



