{% load static %}
{% load get_item %}

const PROTEIN2NAME = {
    'protease': '3CLpro',
    'polymerase': 'RdRp', 
    'helicase': 'Helicase',
    'ace2': 'ACE2',
    'papainlike': 'PLpro',
    'spike_rbd': 'spike RBD',
    'nucleocapsid': 'N protein',
    'tmprss2': 'TMPRSS2'
};

const AA = {
    'ALANINE': 'A',
    'ALA': 'A',
    'ARGININE': 'R',
    'ARG': 'R',
    'ASPARAGINE': 'N',
    'ASN': 'N',
    'ASPARTATE': 'D',
    'ASPARTICACID': 'D',
    'ASP': 'D',
    'ASX': 'B',
    'CYSTEINE': 'C',
    'CYS': 'C',
    'GLUTAMATE': 'E',
    'GLUTAMICACID': 'E',
    'GLU': 'E',
    'GLUTAMINE': 'Q',
    'GLN': 'Q',
    'GLX': 'Z',
    'GLYCINE': 'G',
    'GLY': 'G',
    'HISTIDINE': 'H',
    'HIS': 'H',
    'ISOLEUCINE': 'I',
    'ILE': 'I',
    'LEUCINE': 'L',
    'LEU': 'L',
    'LYSINE': 'K',
    'LYS': 'K',
    'METHIONINE': 'M',
    'MET': 'M',
    'PHENYLALANINE': 'F',
    'PHE': 'F',
    'PROLINE': 'P',
    'PRO': 'P',
    'SERINE': 'S',
    'SER': 'S',
    'THREONINE': 'T',
    'THYMINE': 'T',
    'THR': 'T',
    'TRYPTOPHAN': 'W',
    'TRP': 'W',
    'TYROSINE': 'Y',
    'TYR': 'Y',
    'VALINE': 'V',
    'VAL': 'V',
    'STOP': 'X',
    'TER': 'X',
    '*': 'X',
};

var PROTEIN_TYPE = '';

var pre_pose = "pose_0";

$.ajax({
    url: '{% url "drug-list" %}',
    type: 'GET',
    dataType: "json",
    success: function(data) {
        $(function() {
            $(".term").blur(function(){
                var keyEvent = $.Event("keydown");
                keyEvent.keyCode = $.ui.keyCode.ENTER;
                $(this).trigger(keyEvent);
                return false;
            }).autocomplete({
                source: data.data.symbols,
                autoFocus: true,
                minLength: 2,
                delay: 5,
            });
        });
    },
});

$.ui.autocomplete.filter = function (array, term) {
    var matcher = new RegExp("^" + $.ui.autocomplete.escapeRegex(term), "i");
    return $.grep(array, function (value) {
        return matcher.test(value.label || value.value || value);
    });
};
$.ui.autocomplete.prototype._resizeMenu = function () {
  var ul = this.menu.element;
  ul.outerWidth(this.element.outerWidth());
}

$(function () {
    $('#moreInfoModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget) // Button that triggered the modal
        var drugbankid = button.data('drugbankid') // Extract info from data-* attributes
        // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
        // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
        var cid = button.data('cid')
        var modal = $(this)

        // pubchem
        modal.find('#pubchemTab').children().css('display', 'none');
        modal.find('.pubchem-' + cid).css('display', 'flex');

        // taiwannhi
        modal.find('#taiwannhiTab').children().css('display', 'none');
        modal.find('.taiwannhi-' + cid).css('display', 'flex');
        if (modal.find('.taiwannhi-' + cid).length == 0) {
            modal.find('.taiwannhi-no-data').css('display', 'block');
        }
        modal.find('.taiwannhi-reference').css('display', 'block');

        // drugscreening
        modal.find('#drugscreeningTab').children().css('display', 'none');
        modal.find('.drugscreening-' + drugbankid).css('display', 'flex');
        if (modal.find('.drugscreening-' + drugbankid).length == 0) {
            modal.find('.drugscreening-no-data').css('display', 'block');
        }
        modal.find('.drugscreening-reference').css('display', 'block');

        // gseascore
        modal.find('#gseascoreTab').children().css('display', 'none');
        modal.find('.gseascore-' + drugbankid).css('display', 'flex');
        if (modal.find('.gseascore-' + drugbankid).length == 0) {
            modal.find('.gseascore-no-data').css('display', 'block');
        }
        modal.find('.gseascore-reference').css('display', 'block');
    })
})


$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

$(function() {
    $('#cp2').colorpicker({'color': '#FFC300' ,'format': 'hex'});
});

$(function() {
    $('#filter').on('show.bs.collapse', function () {
        document.getElementById('filterBtn').innerHTML = 'Hide filters';
    });
    $('#filter').on('hidden.bs.collapse', function () {
        document.getElementById('filterBtn').innerHTML = 'Show filters';
    });
})

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function click_drug(cid, protein_type) {
    document.location = '{% url "detail" %}?cid=' + cid + '&protein_type=' + protein_type;
}

function read_json_file(file, callback) {
    var rawFile = new XMLHttpRequest();
    rawFile.overrideMimeType("application/json");
    rawFile.open("GET", file, true);
    rawFile.onreadystatechange = function() {
        if (rawFile.readyState === 4 && rawFile.status == "200") {
            callback(rawFile.responseText);
        }
    }
    rawFile.send(null);
}

function check_file_exist(file) {
    if( file ) {
        var req = new XMLHttpRequest();
        req.open('GET', file, false);
        req.send();
        return req.status==200;
    }
    else {
        return false;
    }
}

function clear_sequence_background_color() {
    // clear_sequence_background_color
    for (var aaDiv of document.getElementsByClassName('sequence-aa')) {
        aaDiv.style.background = "";
    }

}

async function load_compound_structure(cid) {
    // draw compound structure
    await sleep(1000);
    document.getElementById('compound').innerHTML = 'CID: ' + cid;
    var stage = new NGL.Stage("compound", { backgroundColor: "white"});
    stage.removeAllComponents();

    stage.loadFile("{% static 'compound_structure/' %}" + cid + ".pdbqt").then(function(o) {
        o.addRepresentation("ball+stick", {
            multipleBond: "symmetric" 
        })
        o.autoView();
    });
}


function load_docking_structure(cid, protein_type) {

    PROTEIN_TYPE = protein_type;

    event.preventDefault();

    // add protein sequence
    var chain2residue2aa = {}

    document.getElementById('sequence').innerHTML = '';

    read_json_file("{% static 'protein/' %}" + protein_type + ".pdbqt", function(text){

        var lines = text.split("\n");
        for (var i = 0; i < lines.length; i++) {
            var elements = [
                lines[i].substring(0,6).trim(),        // ATOM or HETATM
                lines[i].substring(6,11).trim(),       // Atom name
                lines[i].substring(12,16).trim(),      // Atom serial number
                lines[i].substring(16,17).trim(),      // Alternate location indicator. IGNORED
                lines[i].substring(17,21).trim(),      // Residue name
                lines[i].substring(21,22).trim(),      // Chain identifier
                lines[i].substring(22,26).trim(),      // Residue sequence number
                lines[i].substring(26,27).trim(),      // Code for insertion of residues. IGNORED
                lines[i].substring(30,38).trim(),      // Orthogonal coordinates for X in Angstroms
                lines[i].substring(38,46).trim(),      // Orthogonal coordinates for Y in Angstroms
                lines[i].substring(46,54).trim(),      // Orthogonal coordinates for Z in Angstroms
                lines[i].substring(54,60).trim(),      // Occupancy
                lines[i].substring(60,66).trim(),      // Temperature factor
                lines[i].substring(66,76).trim(),      // Gasteiger PEOE partial charge q
                lines[i].substring(78,80).trim()       // AutoDOCK atom type t
            ]

            if (elements[0] == "ATOM" || elements[0] == "HETATM") {
                var chain = elements[5];
                var aa = elements[4];
                var residue = elements[6];

                if (!(chain in chain2residue2aa)) {
                    chain2residue2aa[chain] = {};
                }
                chain2residue2aa[chain][residue] = AA[aa];
            }
        }

        for (var chain in chain2residue2aa) {
            // console.log(chain);
            var chainDiv = document.createElement("div");
            chainDiv.className = "row";

            var chainTitleDiv = document.createElement("div");
            chainTitleDiv.className = "row";
            chainTitleDiv.innerHTML = "<h6>Chain " + chain + ":</h6>";

            var hr = document.createElement("hr");
            var pre = null;

            for (var residue in chain2residue2aa[chain]) {
                if (typeof residue == "undefined" || typeof chain2residue2aa[chain][residue] == "undefined"){
                    pre = null;
                    continue;
                }
                // console.log(residue);
                var columnDiv = document.createElement("div");
                columnDiv.className = "column";

                var residueDiv = document.createElement("div");
                residueDiv.className = "sequence-residue";
                if (parseInt(residue) % 5 == 0 || parseInt(residue) == 1 || pre != parseInt(residue)-1 || pre == null) {
                    residueDiv.innerHTML = residue;
                }
                else {
                    residueDiv.innerHTML = "&nbsp;";
                }

                var aaDiv = document.createElement("div");
                aaDiv.className = "sequence-aa";
                aaDiv.id = residue + ":" + chain;
                aaDiv.innerHTML = chain2residue2aa[chain][residue];

                columnDiv.appendChild(residueDiv);
                columnDiv.appendChild(aaDiv);

                chainDiv.append(columnDiv);
                pre = residue;
            }
            document.getElementById('sequence').append(chainTitleDiv);
            document.getElementById('sequence').append(chainDiv);
            document.getElementById('sequence').append(hr);

        }
    });

    // draw docking structure
    
    if (check_file_exist("{% static 'docking_structure/' %}" + cid + "/" + protein_type + "/residue_color.json")) {
        document.getElementById('docking-message').innerHTML = 'CID: ' + cid + ' docking with ' + PROTEIN2NAME[protein_type];
        document.getElementById('docking-score-message').innerHTML = 'Pose 1 docking score: {{ detail.pose_score|get_item:"1" }}';

        var stage = new NGL.Stage("docking", { backgroundColor: "white"});
        stage.removeAllComponents();

        read_json_file("{% static 'docking_structure/' %}" + cid + "/" + protein_type + "/residue_color.json", function(text){
            var data = JSON.parse(text);

            stage.loadFile("{% static 'protein/' %}" + protein_type + ".pdbqt", {name: "protein"}).then(function (o) {

                for (var key in data) {
                    o.addRepresentation("surface", {
                        sele: data[key].join(' OR '),
                        color: key,
                        opacity: 0.3,
                    });
                    for (var r of data[key]) {
                        try{
                            document.getElementById(r).style.borderTopColor = (key.toUpperCase() == "#FFFFFF") ? "#CCCCCC" : key;
                            document.getElementById(r).style.borderTopWidth = "5px";
                        }
                        catch (e) {
                            console.log(e);
                        }
                        

                    }
                }

                o.autoView();
            });

        });
        document.getElementById('filterBtn').disabled = false;
        document.getElementById('filterInput').disabled = false;
    }
    else {
        document.getElementById('docking').innerHTML = 'No docking structure data';
        document.getElementById('filterBtn').disabled = true;
        document.getElementById('filterInput').disabled = true;
    }

    stage.loadFile("{% static 'docking_structure/' %}" + cid + "/" + protein_type + "/best.pdbqt", {defaultRepresentation: true, name: "pose_0"});
    
    // add hide arrow eventlistener
    var hide_arrow_btn = document.getElementById("hideArrowBtn");
    hide_arrow_btn.addEventListener("click", async function(e){
        await stage.removeComponent(stage.getComponentsByName("arrow").list[0])
    });

    // add pose buton listener
    var pose_score = {{ detail.pose_score|safe }};

    for (var i = 1; i < 21; i++) {
        var pose_btn = document.getElementById('pose' + i.toString());
        if(!(i.toString() in pose_score)){
            pose_btn.disabled = true;
            continue;
        }
        pose_btn.addEventListener("click", async function(e){

            var pose_score = {{ detail.pose_score|safe }};

            var id = this.id.replace("pose", "");
            await stage.removeComponent(stage.getComponentsByName("arrow").list[0])
            await stage.loadFile("{% static 'docking_structure/' %}" + cid + "/" + protein_type + "/" + cid + "_" + id + ".pdbqt", {defaultRepresentation: true, name: "pose_" + id });
            await stage.removeComponent(stage.getComponentsByName(pre_pose).list[0])

            pre_pose = "pose_" + id;
            var component = stage.getComponentsByName("pose_"+id).list[0];
            var protein_component = stage.getComponentsByName("protein").list[0];

            var cc = component.getCenter();
            var pc = protein_component.getCenter();
            var arrow_s = [cc.x - pc.x + cc.x*1.5, cc.y - pc.y + cc.y*1.5, cc.z - pc.z + cc.z*1.5];
            var arrow_e = [(arrow_s[0] - cc.x)*0.2 + cc.x, (arrow_s[1] - cc.y)*0.2 + cc.y, (arrow_s[2] - cc.z)*0.2 + cc.z]

            var origVector3 = new THREE.Vector3(1,-1,1);
            origVector3.normalize();
            var targetVector3 = new THREE.Vector3(cc.x - arrow_s[0], cc.y - arrow_s[1], cc.z - arrow_s[2]);
            targetVector3.normalize();
            var rotateQuaternion = new THREE.Quaternion();
            rotateQuaternion.setFromUnitVectors(targetVector3, origVector3);

            var shape = new NGL.Shape( "shape" );
            shape.addArrow( arrow_s, arrow_e, [ 0.0784, 0.4784, 0.6078 ], 1.0 );

            var shapeComp = stage.addComponentFromObject(shape, {name: "arrow"});
            shapeComp.addRepresentation("buffer");

            document.getElementById('docking-score-message').innerHTML = 'Pose ' + id + ' docking score: ' + pose_score[id];

            stage.animationControls.rotate(
                rotateQuaternion,
                1000
            );

            stage.animationControls.zoomMove(
                component.getCenter(),
                protein_component.getZoom(),
                1000
            );

            // var html_element = document.createElement("div")
            // html_element.innerText = "Ligand"
            // html_element.style.color = "black"
            // html_element.style.backgroundColor = "royalblue"
            // html_element.style.padding = "8px"

            // component.addAnnotation(component.getCenter(), html_element)


            // stage.animationControls.move(
            //   component.getCenter(),
            //   500
            // );
            // var origVector3 = new THREE.Vector3(0,0,1);
            // var targetVector3 = new THREE.Vector3();
            // var protein_center = protein_component.getCenter();
            // var ligand_center = component.getCenter();
            // var stage_center = stage.getCenter()
            // targetVector3.subVectors(protein_center, ligand_center).normalize();
            // var targetQuaternion = new THREE.Quaternion();
            // targetQuaternion.setFromUnitVectors(origVector3, targetVector3);

            // stage.animationControls.rotate(
            //   targetQuaternion,
            //   500
            // );
        })
    }

    // add filter input and button
    var filter_btn = document.getElementById('filterBtn');
    var filter_input = document.getElementById('filterInput');
    var filter = null;

    filter_input.addEventListener('keypress', function(e){
        if (e.keyCode == 13){
            e.preventDefault();
            if (filter != null) {
                filter.setVisibility(false);
            }
            clear_sequence_background_color();
            var filter_color = document.getElementById("filterColorInput").value;

            stage.loadFile("{% static 'protein/' %}" + PROTEIN_TYPE + ".pdbqt").then(function (o) {

                filter = o.addRepresentation("surface", {
                    sele: filter_input.value,
                    color: filter_color,
                    opacity: 0.5,
                });

                var selection = new NGL.Selection(filter_input.value);
                var structionView = o.structure.getView(selection);
                structionView.eachResidue(function (rp){
                    document.getElementById(rp.resno + ":" + rp.chainname).style.background = filter_color;
                });

                o.autoView();
            });

        }
    });

    filter_btn.addEventListener("click", function(e){ 
        if (filter != null) {
            filter.setVisibility(false);
        }
        clear_sequence_background_color();
        var filter_color = document.getElementById("filterColorInput").value;

        stage.loadFile("{% static 'protein/' %}" + PROTEIN_TYPE + ".pdbqt").then(function (o) {
            filter = o.addRepresentation("surface", {
                sele: filter_input.value,
                color: filter_color,
                opacity: 0.5,
            });

            var selection = new NGL.Selection(filter_input.value);
            var structionView = o.structure.getView(selection);
            structionView.eachResidue(function (rp){
                document.getElementById(rp.resno + ":" + rp.chainname).style.background = filter_color;
            });

            o.autoView();
        });

    });
}

function apply_filter(){
    // show loading
    document.getElementById('topListLoading').style.display="inline-block";

    var table = document.getElementById('topListTable').getElementsByTagName('tbody')[0];

    var xhr = new XMLHttpRequest();
    // we defined the xhr

    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var data = JSON.parse(this.responseText);

            for (var i = table.rows.length; i > 0; i--) {
                table.deleteRow(-1);
            }
            for (var i = 0; i < data.length; i++) {
                var row = table.insertRow(-1);

                // #
                var th = document.createElement('th');
                th.innerHTML = i + 1;
                th.setAttribute('scope', 'row');
                row.appendChild(th);

                // drug name
                var cell = row.insertCell(-1);
                var value = data[i]['drug__drug_name'];
                cell.setAttribute('data-toggle', 'tooltip');
                cell.setAttribute('data-placement', 'top');
                cell.setAttribute('title', value);

                cell.innerHTML = '<a href="{% url "search" %}?term=' + value + '">' + value + '</a>';

                // docking score
                var cell = row.insertCell(-1);
                var value = data[i]['docking_score'];

                cell.innerHTML = value;

                // protein type
                var cell = row.insertCell(-1);
                var value = data[i]['protein_type'];

                cell.innerHTML = '<span class="' + value + ' protein">' + PROTEIN2NAME[value] + '</span>';

                // popular views
                var cell = row.insertCell(-1);
                var value = data[i]['drug__popular_views'];

                cell.innerHTML = value;

                // drug from 
                var cell = row.insertCell(-1);
                var values = data[i]['drug__drug_source'];

                for (var value of values.split(',')) {
                    if (value == 'l4200' && !values.includes('fda')){
                        cell.innerHTML += '<span class="' + 'fda' + ' drug-source mr-1 ml-1">' + 'FDA' + '</span>';
                    }
                    else if (value != 'l4200'){
                        cell.innerHTML += '<span class="' + value + ' drug-source mr-1 ml-1">' + value.toUpperCase() + '</span>';
                    }
                }

            }


            // hide loading
            document.getElementById('topListLoading').style.display="none";

            $(function () {
                $('[data-toggle="tooltip"]').tooltip();
            })
        }

        // end of state change: it can be after some time (async)
    };
    var protein_type = document.getElementById('proteinTypeSelect').value;
    var sort_by = document.getElementById('sortBySelect').value; 
    var rows = document.getElementById('rowsSelect').value;
    var url = '{% url "top-list" %}?protein_type=' + protein_type + '&sort_by=' + sort_by + '&rows=' + rows;

    xhr.open('GET', url, true);
    xhr.send();
}
