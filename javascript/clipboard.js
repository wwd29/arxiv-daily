new ClipboardJS("#copy", {
    text: function(trigger) {
        var date = document.querySelector("h1").innerText;
        var res = "[[" + date + "]]\n\n";
        var input_checkbox = document.querySelectorAll('input[type="checkbox"]');
        var input_text = document.querySelectorAll('input[type="text"]');
        for (var i = 0; i < input_checkbox.length; i++) {
            if (input_checkbox[i].checked) {
                res += "- " + input_checkbox[i].nextSibling.nodeValue + " " + input_text[i].value + "\n";
            }
        }
        res += "\n";
        return res;
    }
}).on("success", function(e) {
    e.clearSelection()
});