new ClipboardJS("#copy",{text:function(trigger){var res="[[2023-07-28]]\n\n";var input=document.querySelectorAll("input");for(var i=0;i<input.length;i++){if(input[i].type=="checkbox"&&input[i].checked){res+="- "+input[i].nextSibling.nodeValue+"\n"}}res+="\n";return res}}).on("success",function(e){e.clearSelection()});
