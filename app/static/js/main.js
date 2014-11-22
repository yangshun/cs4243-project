var CANVAS_WIDTH = 828;
var CANVAS_HEIGHT = 495;

var BOUNDARY_RECT_TOP_LEFT_X = 237;
var BOUNDARY_RECT_TOP_LEFT_Y = 88;
var BOUNDARY_RECT_BOTTOM_LEFT_X = 700;
var BOUNDARY_RECT_BOTTOM_LEFT_Y = 391;
var BOUNDARY_RECT_REAL_WIDTH = 2095;
var BOUNDARY_RECT_REAL_HEIGHT = 740;
var BOUNDARY_RECT_FILL_SELECTED = 'rgba(0,188,140,0.2)';
var BOUNDARY_RECT_FILL_DISABLED = 'rgba(178,74,24,0.2)';

var POINT_RADIUS = 5;
var POINT_FILL_COLOR = 'red';
var POINT_LABEL_FONT = 'sans-serif';
var POINT_LABEL_FONT_SIZE = 14;
var POINT_LABEL_FONT_WEIGHT = 'bold';

var CAMERA_DEFAULT_HEIGHT = 40;

angular.module('CameraApp', []).config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[').endSymbol(']]');
});

function CameraController ($scope, $http) {
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
    boundaryRect.set({
      selectable: $scope.boundaryRectEditable,
      fill: $scope.boundaryRectEditable ? BOUNDARY_RECT_FILL_SELECTED : BOUNDARY_RECT_FILL_DISABLED,
      hasControls: $scope.boundaryRectEditable,
      hasBorders: $scope.boundaryRectEditable
    });
    canvas.renderAll();
  };

  $scope.renderBoundaryRect = function () {
    boundaryRect.set(getBoundaryRectProps());
    canvas.renderAll();
  };

  $scope.pathPoints = [];

  canvas.on('mouse:down', function(options) {
    if ($scope.boundaryRectEditable) {
      // Prevent point from being added when editing boundary rect
      return;
    }

    var point = options.e;

    var circle = new fabric.Circle({
      radius: POINT_RADIUS, 
      fill: POINT_FILL_COLOR, 
      left: point.offsetX - POINT_RADIUS,
      top: point.offsetY - POINT_RADIUS,
      selectable: false
    });
    circle.z = CAMERA_DEFAULT_HEIGHT; // Set default z-value for video;

    var label = new fabric.Text(($scope.pathPoints.length + 1).toString(), {
      fontWeight: POINT_LABEL_FONT_WEIGHT,
      fontSize: POINT_LABEL_FONT_SIZE,
      fontFamily: POINT_LABEL_FONT,
      left: point.offsetX - POINT_RADIUS/2,
      top: point.offsetY + POINT_RADIUS,
    });
    $scope.pathPoints.push({
      point: circle,
      label: label
    })
    canvas.add(circle);
    canvas.add(label);
    $scope.$apply();
  });

  $scope.deletePoint = function (index) {
    var pt = $scope.pathPoints[index];
    canvas.remove(pt.point);
    canvas.remove(pt.label);
    $scope.pathPoints.splice(index, 1);
    for (var i = 0; i < $scope.pathPoints.length; i++) {
      $scope.pathPoints[i].label.setText((i+1).toString());
    }
    canvas.renderAll();
  }

  $scope.normalizePathPoint = function (point) {
    var x = point.left - $scope.topLeft.x;
    var y = point.top - $scope.topLeft.y;
    var boundaryBoxX = x;
    var boundaryBoxY = y;
    return {
      x: Math.round(((-boundaryBoxY/boundaryRect.currentHeight) + 0.5) * $scope.boundaryHeight, 2),
      y: Math.round(-boundaryBoxX/boundaryRect.currentWidth * $scope.boundaryWidth, 2),
      z: point.z 
    };
  }

  function normalizePathPoints (pathPoints) {
    return pathPoints.map(function (point) {
      // Map to boundary box coordinates
      return $scope.normalizePathPoint(point);
    });
  }

  $scope.renderingVideo = false;
  $scope.cameraLookingForward = false;

  $scope.renderVideoWithPath = function () {
    var pathPoints = $scope.pathPoints.map(function (pt) {
      return pt.point;
    });
    var cameraPathPoints = normalizePathPoints(pathPoints);

    $scope.renderingVideo = true;
    $http.post('/generate_video', {
      camera_path: cameraPathPoints,
      camera_looking_forward: $scope.cameraLookingForward,
      file_name: new Date().getTime()
    }).success(function (res, status, headers, config) {
      if (res.status === 'success') {
        $scope.renderingVideo = false;
        var video = res.video;
        var $videoPlayer = $('.video-player');
        $videoPlayer.width(video.width);
        $videoPlayer.height(video.height);
        $videoPlayer.attr('src', video.src);
        $('#video-modal').modal();
      }
    }).error(function (res, status, headers, config) {
      alert('Rendering failed');
      $scope.renderingVideo = false;
    });
  }

  $scope.getRenderVideoButtonState = function () {
    var pathObject = canvas.getActiveObject();
    return pathObject && pathObject !== boundaryRect && pathObject.path;
  };

  toggleBoundaryRectEditing($scope.boundaryRectEditable);
  boundaryRect.set(getBoundaryRectProps());

  $scope.toggleBoundaryRectEditing = toggleBoundaryRectEditing;

  fabric.Image.fromURL('/static/img/aerial-view.jpg', function (img) {
    img.set('selectable', false);
    canvas.add(img);
    canvas.add(boundaryRect);
  });
}
