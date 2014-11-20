var CANVAS_WIDTH = 828;
var CANVAS_HEIGHT = 495;

var BOUNDARY_RECT_TOP_LEFT_X = 51;
var BOUNDARY_RECT_TOP_LEFT_Y = 88;
var BOUNDARY_RECT_BOTTOM_LEFT_X = 782;
var BOUNDARY_RECT_BOTTOM_LEFT_Y = 382;
var BOUNDARY_RECT_REAL_WIDTH = 2095;
var BOUNDARY_RECT_REAL_HEIGHT = 740;

angular.module('CameraApp', []).config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
});

function CameraController ($scope) {
  var canvas = new fabric.Canvas('map-container', {
    width: CANVAS_WIDTH,
    height: CANVAS_HEIGHT
  });

  // canvas.on('mouse:down', function (options) {
  //   console.log(options.e.clientX, options.e.clientY);
  // });

  $scope.topLeft = {x: BOUNDARY_RECT_TOP_LEFT_X, y: BOUNDARY_RECT_TOP_LEFT_Y};
  $scope.bottomRight = {x: BOUNDARY_RECT_BOTTOM_LEFT_X, y: BOUNDARY_RECT_BOTTOM_LEFT_Y};
  $scope.boundaryWidth = BOUNDARY_RECT_REAL_WIDTH;
  $scope.boundaryHeight = BOUNDARY_RECT_REAL_HEIGHT;
  $scope.boundaryRectEditable = true;

  function getBoundaryRectProps () {
    return {
      width: $scope.bottomRight.x - $scope.topLeft.x, 
      height: $scope.bottomRight.y - $scope.topLeft.y,
      left: $scope.topLeft.x, 
      top: $scope.topLeft.y
    }
  }

  canvas.on('object:modified', function (object) {
    updateBoundaryRect(object.target);
  });

  function updateBoundaryRect (rect) {
    $scope.topLeft.x = Math.round(rect.left);
    $scope.topLeft.y = Math.round(rect.top);
    $scope.bottomRight.x = Math.round(rect.left + rect.currentWidth);
    $scope.bottomRight.y = Math.round(rect.top + rect.currentHeight);
    $scope.$apply();
  }

  function toggleBoundaryRectEditing (state) {
    $scope.boundaryRectEditable = state ? state : !$scope.boundaryRectEditable;
    if ($scope.boundaryRectEditable) {
      toggleDrawingPath(false);
    }
    boundaryRect.set({
      selectable: $scope.boundaryRectEditable,
      fill: $scope.boundaryRectEditable ? 'rgba(0,188,140,0.2)' : 'rgba(178,74,24,0.2)',
      hasControls: $scope.boundaryRectEditable,
      hasBorders: $scope.boundaryRectEditable
    });
    canvas.renderAll();
  };

  $scope.renderBoundaryRect = function () {
    boundaryRect.set(getBoundaryRectProps());
    canvas.renderAll();
  };

  $scope.isDrawingPath = false;

  function toggleDrawingPath (state) {
    $scope.isDrawingPath = state ? state: !$scope.isDrawingPath;
    if ($scope.isDrawingPath) {
      toggleBoundaryRectEditing(false);
    }
    canvas.isDrawingMode = $scope.isDrawingPath;
    canvas.renderAll();
  };

  var boundaryRect = new fabric.Rect({
    fill: 'rgba(0,188,140,0.2)',
    lockRotation: true
  });

  toggleDrawingPath($scope.isDrawingPath);
  toggleBoundaryRectEditing($scope.boundaryRectEditable);
  boundaryRect.set(getBoundaryRectProps());

  $scope.toggleBoundaryRectEditing = toggleBoundaryRectEditing;
  $scope.toggleDrawingPath = toggleDrawingPath;

  fabric.Image.fromURL('/static/img/aerial-view.jpg', function (img) {
    img.set('selectable', false);
    canvas.add(img);
    canvas.add(boundaryRect);
  });
}
