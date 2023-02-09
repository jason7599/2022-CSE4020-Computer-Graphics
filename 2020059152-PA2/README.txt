2022 CSE4020 Computer Graphics
PA2 (Cow Roller Coaster)
by Oh Juyoung (#200200591592)
===============================

1. onMouseDrag , line 391 {
In order to implement vertical dragging, I had to create a new plane that was perpendicular to the ray 
direction. There also was a problem in H_DRAG as the intersection check was being done on the plane which
contained pp.cowPickPosition, which is only initialized when the mouse is clicked. This meant that whenever
the dragging exited V_DRAG mode and reentered the H_DRAG mode, the cow's y coordinate would jump back 
to where it was picked up. To fix this problem, I made a new global variable "currentPos" which kept updating
whenever onMouseDrag was called. So instead of pp.cowPickPosition as the point the plane would contain(the 2nd
arguement for the class Plane), I set it to currentPos which turned out to work. When in V_DRAG, it was important to
not change the cow's x and z coordinates. So I made sure to update only the value in index 1, the y position. }

2. onMouseButton , line 367 {
Modifying onMouseButton was much more complex than I'd expected. First I implemented the control points
and duplication to happen whenever the left mouse button was up(GLFW_UP) after being clicked. For this,
I made a global array "controlPoints", and appended the cow each time the click ended. This posed a problem -
a control point would be added when the initial click on the cow. To fix this, I declared a global boolean "initState"
which would be set to False after the first click on the cow. Everytime a control point was added, I made it
check the length of the array controlPoints. When the length reaches 6, I set "AnimState", another global boolean 
variable I declared, to True and assigned "animStartTime" with glfw.get_time() and also set it global. Since no more
mouse inputs should be taken while the animation was taking place, I added a line of code at the beginning of the
function to check if AnimState was True, and if so ended the function by using return. For the animation itself, I made
a global copy of the cow, named "cursorCow" and assigned it to controlPoints[0], the first control point of the array.
(I named it cursorCow for the sole reason that "cursor" means runner in Latin. It soon became very confusing but I
stuck with it anyways)}

3. display , line 233 {
Operations in display mainly consists of two parts: if AnimState, and if not. If not AnimState, simply draw the main cow
(cow2ld), and all the duplicate cows in controlPoints. For cows in controlPoints, the bounding box was not drawn. If
AnimState, however, wasn't as simple. First, I updated the global variable "animTime" with glfw.get_time()-animStartTime
and assigned a local variable "startIndex" as math.floor(animsTime). Note that, contrary to what the term "index" might suggest, 
startIndex can go over 5, the last index of the array controlPoints. For the spline calculation, I used catmull rom conversion. 
So I made a global matrix "catmullRom". Next I declared a row vector "T" consisting of t^3, t^2, t^1 and t^0. t here I assigned 
to animTime-startIndex so that the value of t would always be in the range of (0,1). Then I declared a column vector "K" which 
would consist of k0, k1, k2 and k3(the point before, the current point, the next point, and the one after it). In order to use 
"startIndex" as an actual index, I used the modular operation here. With T, catmullRom and K I could calculate cursorCow's next 
position the next iteration. But before assigning cursorCow to this next position, I first stored this position in a variable 
"nextCow", and assigned a variable "direction" to normalize(getTranslation(nextCow)-getTranslation(cursorCow)). Since 
cursorCow's position was yet to be updated at this stage, direction would point to where the cow should move next. So 
direction would now be cursorCow's new local X axis. And with a series of cross product operations, I was able to calculate 
cursorCow's new local Y and Z axes. I then declared a 3 by 3 matrix for cursorCow's rotation, and assigned the 3 columns with 
these new axes. Only after setting nextCow's rotation with R, would cursorCow be updated to nextCow. To check whether the
animation has finished, I compared startIndex to 18. If startIndex was less than 18, the animation should continue, so simply
draw the cursorCow but without the bounding box. If startIndex is equal to 18, set AnimState to False, set cow2wld to 
controlPoints[0], and clear controlPoints.
}

4. setRotation, line 77 {
A function I made that replaces the rotation part of a homogeneous matrix.
}





