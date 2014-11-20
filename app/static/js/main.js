$(function () {
  var canvas = new fabric.Canvas('map-container', {
    width: 828,
    height: 495
  });


  fabric.Image.fromURL('/static/img/aerial-view.jpg', function (img) {
    img.set('selectable', false);
    canvas.add(img);
  });

});
