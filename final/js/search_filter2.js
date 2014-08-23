// Author: Silvia Chang
// Scripts to handle the search_filter_page.html

// this function executes our search via an AJAX call
function runSearch() {
    // hide and clear the previous results, if any
    $("#results").hide();
    $("tbody").empty();
    
    // transforms all the form parameters into a string we can send to the server
    var frmStr = $("#search_form").serialize();
    console.log(frmStr);
    $.ajax({
        url: './final_search_id.cgi',
        dataType: 'json',
        data: frmStr,
        success: function(data, textStatus, jqXHR) {
            processJSON(data);
        },
        error: function(jqXHR, textStatus, errorThrown){
            alert("Failed to perform gene search! textStatus: (" + textStatus +
                  ") and errorThrown: (" + errorThrown + ")");
        }
    });
}

// this function executes a search by filtering values
function runFilter() {
    $("#results").hide();
    $("tbody").empty();
    
    // transforms all the form parameters into a string we can send to the server
    var frmStr = $("#filter_form").serialize();
    frmStr = frmStr.replace(/\%\d+/, '@');
    console.log(frmStr);
    $.ajax({
        url: './final_filter.cgi',
        dataType: 'json',
        data: frmStr,
        success: function(data, textStatus, jqXHR) {
            processJSON(data);
        },
        error: function(jqXHR, textStatus, errorThrown){
            alert("Failed to perform gene search! textStatus: (" + textStatus +
                  ") and errorThrown: (" + errorThrown + ")");
        }
    });
}

//this function executes the search via an AJAX call to give suggestions via .autocomplete()
function autoFill() {
	$( '#search_gene_id' ).autocomplete({
		source: function( request, response ) {
			var maxRows = 10;
			var some_id = request.term;
			var paramStr = "maxRows=" + maxRows + "&some_id=" + some_id;
			$.ajax({
				url: './final_search_id.cgi',
				dataType: 'json',
				data: paramStr,
				contentType: 'application/json; charset=utf-8',
				success: function( data ) {
					response( $.map( data.matches, function( item ) {
						return {
							value: item.GeneID,
							label: item.TranscriptID
						}
					}));
				}
			});
		},
		minLength: 2,
		select: function(event, ui) {
//			 $(this).val(ui.item.label || ui.item.value);
			$(this).val(ui.item.value);
		}
//		open: function() {
//			$( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
//		},
//		close: function() {
//			$( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
//		}
	});
}

// this processes a passed JSON structure representing gene matches and draws it
//  to the result table
function processJSON( data ) {
    // set the span that lists the match count
    $('#match_count').text( data.match_count );
    
    // this will be used to keep track of row identifiers
    var next_row_num = 1;
    
    // iterate over each match and add a row to the result table for each
    $.each( data.matches, function(i, item) {
        var this_row_id = 'result_row_' + next_row_num++;
    
        // create a row and append it to the body of the table
        $('<tr/>', { "id" : this_row_id } ).appendTo('tbody');
        
        // add the geneid column
        $('<td/>', { "text" : item.GeneID } ).appendTo('#' + this_row_id);
        
        // add the transcriptid column
        $('<td/>', { "text" : item.TranscriptID } ).appendTo('#' + this_row_id);
        
        // add the isoform% column
        $('<td/>', { "text" : item.IsoPct } ).appendTo('#' + this_row_id);
        
        // add the gene_tpm column
        $('<td/>', { "text" : item.Gene_TPM } ).appendTo('#' + this_row_id);
        
        // add the trans_tpm column
        $('<td/>', { "text" : item.Trans_TPM } ).appendTo('#' + this_row_id);
        
        // add the gene_FPKM column
        $('<td/>', { "text" : item.Gene_FPKM } ).appendTo('#' + this_row_id);
        
        // add the trans_FPKM column
        $('<td/>', { "text" : item.Trans_FPKM } ).appendTo('#' + this_row_id);
        
        if(next_row_num == 100) {
        	return false;
        }

    });
    
    // now show the result section that was previously hidden
    $('#results').show();
}



// run our javascript once the page is ready
$(document).ready( function() {
	// define what should happen when a user clicks submit on our search form
    $('#find').click( function() {
        runSearch();
        return false;  // prevents 'normal' form submission
    });
    $(function(){
		autoFill();
	});
    $('#filter').click( function() {
    	runFilter();
    	return false;
    })
});