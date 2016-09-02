function createTemplate(){
	return '<li class="{{imageName}}">'
                   + '<div class="img" style="background-image: url(' + "./img/pane/pane{{paneNumber}}.jpeg" +')"></div>'
                   + '<div></div>'
                   + '<div class="like"></div>'
                   + '<div class="dislike"></div>'
                + '</li>';	
 
}

// function getCount(){
//       var myObject, f, filesCount;
//       myObject = new ActiveXObject("Scripting.FileSystemObject");
//       f = myObject.GetFolder('./img/pane');
//       filesCount = f.files.Count;
//       document.write("The number of files in this folder is: " + filesCount);
//       return filesCount;
// }

function generateLi(){
	// var imageCount = getCount();
	var temp = '';
	for(var i= 1; i<=36; i++){
		var template = createTemplate();
		template  = template.replace('{{imageName}}','pane'+i);
		template  = template.replace('{{paneNumber}}',i);
		temp+=template;
	}
	return temp;
}

function createslideDiv(){
	var list = generateLi();
	$("#tinderslide ul").append(list);
}

createslideDiv(); 
