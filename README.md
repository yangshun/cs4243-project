cs4243-project
==============

### Installation

The project is made as a web application based on flask, a Python web framework.
Firstly, install flask if it is not already installed:
```
pip install flask
```

To run the flask application, navigate to the root directory and do:
```
python server.py
```
The app will be running on `http://localhost:8080/`.

### Using the Application

We have used two images for demonstration of our application:

##### 1. Carnegie Mellon University
Navigate to `http://localhost:8080/#cmu`.

##### 2. Stanford
Navigate to `http://localhost:8080/#stanford`.

Click on the **Plan View** tab and click within the red boundary rectangles to specify points of the bezier curve.
Once more than 4 points are specified, the **Render Video** button will be enabled. Click on it to generate a video based on the path you have specified. After the video is fully generated, it will be shown in a window.

The generated videos will be inside `app/static/video/`.

### Team Members
- Le Minh Tu
- Tay Yang Shun
- Nguyen Trung Hieu
- Tay Xiu Li
