
// Work around for cors origin preventing the <use> required by svg when provided from a remote server 
// for more information reads the docs at https://css-tricks.com/ajaxing-svg-sprite/

var ajax = new XMLHttpRequest();
ajax.open(
  "GET", "https://movie-rater.s3.amazonaws.com/static/sprites/sprite.svg", 
  true
  );
ajax.send();
ajax.onload = function(e) {
  var div = document.createElement("div");
  div.innerHTML = ajax.responseText;
  document.body
  .insertBefore(
    div, 
    document.body.childNodes[0]
    );
}