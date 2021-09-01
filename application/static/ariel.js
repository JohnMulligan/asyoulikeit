  //from https://stackoverflow.com/questions/52630947/window-getselection-include-html-tag
  $(function() {
  	
  	$('#maintext').on('click', 'a.T', function text_select(event) {
  		var id = event.target.id;
  		$('#correlatedtexts').html("<center>...Loading...</center>");
  		$.get( "/correlated_texts/"+id+"/10", function( data ) {
			$('#correlatedtexts').html(data);
		});
		$.get("/get_gamestate_link/"+id+"/10",function( data ) {
			$('#share').html(data);
		});
		$('#correlatedtexts').scrollTo('#c_top');
		$('#articles').html('');
		highlight_selection(id,9)
  	});
  	
  	//get correlated texts html block
	//& update
  	$('#correlatedtexts').on('click', 'a.C',function infratext_select(event) {
  		$('#correlatedtexts').html("<center>...Loading...</center>");
  		$('#maintext').html("<center>...Loading...</center>");
  		$('#playname').html("<center>...Loading...</center>");
  		t= event.target.id.split("-");
  		var n=t[0];
  		var id = t[1];
  		href="/?rowid="+id+"&n="+n;
  		console.log(href)
  		window.location.replace(href)
 	});
  	
  	//get articles html block
  	//& update
  	$('#correlatedtexts').on('click','a.A',function articlelist_select(event) {
  		$('#articles').html('');
  		t= event.target.id.split("-");
  		var source_id=t[0];
  		var target_id=t[1];
  		$('#articles').html("<span class=\"articletext\"><center>...Loading...</center></span>");  		
  		t=event.target.id.split("-");
  		var n=t[0];
  		var id = t[1];
  		$.get("/get_articles/"+source_id+"/"+target_id+"/10",function( data ) {
			$('#articles').html(data);
		});
		
 	});
 	
 	$('#correlatedtexts').on('click','a.c_top',
		function clearselection(event) {
			$('#correlatedtexts').html('');
			$('a.T').css('background','none');
			$('#articles').html('');
 	});
 	
 	function resize() {
 		var wheight=window.innerHeight;
  		var bodytopoffset=$('body').offset().top;
  		var margin_top=Number($('body').css('margin-top').replace('px',''));
  		var margin_bottom=Number($('body').css('margin-bottom').replace('px',''));
 		var footerheight=$('#footer').height();
 		var headerheight=$('#header').height();
 		var maincontainerheight=wheight-footerheight-headerheight-(bodytopoffset*2)-margin_top-margin_bottom;
		$('#maincontainer').height(maincontainerheight);	
 	}
 	
 	//from https://www.sitepoint.com/url-parameters-jquery/
 	$.urlParam = function(name){
		try {
			var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
			return results[1] || 0;
		}
		catch {
			return null;
		}
	};
	
 	//from https://stackoverflow.com/questions/8069315/create-array-of-all-integers-between-two-numbers-inclusive-in-javascript-jquer/33457557
 	function highlight_selection(rowid,n) {
 		$.getJSON("/get_selection/"+rowid+"/"+n+"",function( data ) {
			rowids=data.s;
			$('a.T').css('background','none');
			rowids.forEach(async function (rowid){
				$('#'+rowid.toString()).css('background','#f2a0a0')
			});
		});
 	};
 	
 	function doc_init() {
 		resize();
 		var rowid=$.urlParam('rowid');
 		if (rowid != null) {
 			$('#maintext').scrollTo('#'+rowid.toString());
 			highlight_selection(rowid,9);
 		} else {
 			$('#articles').load('static/welcome.html')
 		};
		$('#correlatedtexts').scrollTo('#c_top');
 	};
 	
   	$(window).on("resize",resize);
   	$(document).ready(doc_init);
  
  }); 
