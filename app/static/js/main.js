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
  canvas = new fabric.Canvas('map-container', {
    width: CANVAS_WIDTH,
    height: CANVAS_HEIGHT
  });

  $scope.topLeft = {x: BOUNDARY_RECT_TOP_LEFT_X, y: BOUNDARY_RECT_TOP_LEFT_Y};
  $scope.bottomRight = {x: BOUNDARY_RECT_BOTTOM_LEFT_X, y: BOUNDARY_RECT_BOTTOM_LEFT_Y};
  $scope.boundaryWidth = BOUNDARY_RECT_REAL_WIDTH;
  $scope.boundaryHeight = BOUNDARY_RECT_REAL_HEIGHT;
  $scope.boundaryRectEditable = false;

  var boundaryRect = new fabric.Rect({
    fill: 'rgba(0,188,140,0.2)',
    lockRotation: true
  });

  function getBoundaryRectProps () {
    return {
      width: $scope.bottomRight.x - $scope.topLeft.x, 
      height: $scope.bottomRight.y - $scope.topLeft.y,
      left: $scope.topLeft.x, 
      top: $scope.topLeft.y
    }
  }

  canvas.on('object:modified', function (object) {
    if (object.target === boundaryRect) {
      updateBoundaryRect(object.target);
    }
  });

  function updateBoundaryRect (rect) {
    $scope.topLeft.x = Math.round(rect.left);
    $scope.topLeft.y = Math.round(rect.top);
    $scope.bottomRight.x = Math.round(rect.left + rect.currentWidth);
    $scope.bottomRight.y = Math.round(rect.top + rect.currentHeight);
    $scope.$apply();
  }

  function toggleBoundaryRectEditing (state) {
    $scope.boundaryRectEditable = typeof state !== 'undefined' ? state : !$scope.boundaryRectEditable;
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
    $scope.isDrawingPath = typeof state !== 'undefined' ? state: !$scope.isDrawingPath;
    if ($scope.isDrawingPath) {
      toggleBoundaryRectEditing(false);
    } else {
      canvas.getObjects().filter(function (obj) {
        return !!obj.path;
      }).forEach(function (obj) {
        obj.set({
          lockMovementX: true,
          lockMovementY: true,
          lockRotation: true,
          lockScalingX: true,
          lockScalingY: true
        });
      });
    }
    canvas.isDrawingMode = $scope.isDrawingPath;
    canvas.renderAll();
  }

  $('html').keydown(function (e) {
    if (e.keyCode == 8) {
      var pathObject = canvas.getActiveObject();
      if (pathObject && pathObject !== boundaryRect && pathObject.path) {
        e.preventDefault();
        canvas.fxRemove(pathObject);
      }
    }
  });

  $('input').focus(function () {
    canvas.deactivateAll().renderAll();
  });

  function normalizePathPoints (pathPoints) {
    pathPoints.forEach(function (point) {
      // Map to boundary box coordinates
      point.x -= $scope.topLeft.x;
      point.y -= $scope.topLeft.y;
    });
    pathPoints.forEach(function (point) {
      // Map to camera coordinates
      var boundaryBoxX = point.x;
      var boundaryBoxY = point.y;
      point.x = Math.round(((-boundaryBoxY/boundaryRect.currentHeight) + 0.5) * $scope.boundaryHeight, 2);
      point.y = Math.round(-boundaryBoxX/boundaryRect.currentWidth * $scope.boundaryWidth, 2);
    });
    return pathPoints;
  }

  $scope.renderVideoWithPath = function () {
    var pathObject = canvas.getActiveObject();
    if (!pathObject) {
      alert('You must select one camera path!');
      return;
    }
    var paths = [];
    pathObject.path.forEach(function (point) {
      if (point.length === 3) {
        paths.push({
          x: point[1],
          y: point[2]
        });
      } else if (point.length === 5) {
        paths.push({
          x: point[1],
          y: point[2]
        });
        paths.push({
          x: point[3],
          y: point[4]
        });
      }
    });
    var cameraPathPoints = normalizePathPoints(paths);
    console.log(cameraPathPoints);
    // Do something with cameraPathPoints.
  }

  $scope.getRenderVideoButtonState = function () {
    var pathObject = canvas.getActiveObject();
    return pathObject && pathObject !== boundaryRect && pathObject.path;
  };

  $scope.pathSelected = false;
  canvas.on('object:selected', function () {
    $scope.pathSelected = $scope.getRenderVideoButtonState();
    $scope.$apply();
  });

  canvas.on('selection:cleared', function () {
    $scope.pathSelected = $scope.getRenderVideoButtonState();
    $scope.$apply();
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
