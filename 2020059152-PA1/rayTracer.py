# !/usr/bin/env python3
# -*- coding: utf-8 -*
# see examples below
# also read all the comments below.

import imghdr
import math
import os
import sys
import pdb  # use pdb.set_trace() for debugging
import code  # or use code.interact(local=dict(globals(), **locals()))  for debugging.
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

class Color:
    def __init__(self, R, G, B):
        self.color = np.array([R, G, B]).astype(float)

    # Gamma corrects this color.
    # @param gamma the gamma value to use (2.2 is generally used).
    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma
        self.color = np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0, 1) * 255).astype(np.uint8)
    
def rayTrace_Sphere(d, p, radius,center):
    newP = center - p
    tm=np.dot(newP,d)
    lm_squared=np.dot(newP,newP)-tm**2
    #print("tm:", tm)
    if tm < 0:
        return None #wrong direction
    else:
        if lm_squared > radius**2: #no intersection
            return None
        elif lm_squared == radius**2: #on the verge
            return None
        else:       
           return tm - np.sqrt(radius**2-lm_squared)

def rayTrace_Box(d,p,minPt,maxPt):

    #for i in range(3):
        #if d[i] == 0:
            #return tEnter

    txMin=(minPt[0]-p[0])/d[0]
    txMax=(maxPt[0]-p[0])/d[0]

    if txMin > txMax:
        txMin,txMax=txMax,txMin

    tyMin=(minPt[1]-p[1])/d[1]
    tyMax=(maxPt[1]-p[1])/d[1]

    if tyMin > tyMax:
        tyMin,tyMax=tyMax,tyMin

    if txMin > tyMax or tyMin > txMax:
        return None

    if tyMin > txMin:
        txMin=tyMin
    if tyMax < txMax:
        txMax=tyMax
    
    tzMin=(minPt[2]-p[2])/d[2]
    tzMax=(maxPt[2]-p[2])/d[2]

    if tzMin > tzMax:
        tzMin,tzMax=tzMax,tzMin

    if txMin > tzMax or tzMin >txMax:
        return None
    
    if tzMin > txMin:
        txMin=tzMin
    if tzMax < txMax:
        txMax = tzMax

    if txMin < 0:
        return None

    return txMin

def normalize(ray):
    return ray / np.sqrt(ray @ ray)

def main():
    #scene=input("choose a scene: ")
    tree = ET.parse(sys.argv[1])
    #tree = ET.parse(scene+".xml")
    root = tree.getroot()

    # set default values
    viewDir = np.array([0, 0, -1]).astype(float)
    viewUp = np.array([0, 1, 0]).astype(float)
    viewProjNormal = -1 * viewDir  # you can safely assume this. (no examples will use shifted perspective camera)
    viewWidth = 1.0
    viewHeight = 1.0
    projDistance = 1.0
    intensity = np.array([1, 1, 1]).astype(float)  # how bright the light is.
    print(np.cross(viewDir, viewUp));

    imgSize = np.array(root.findtext('image').split()).astype(int)
    for c in root.findall('camera'):
        viewPoint = np.array(c.findtext('viewPoint').split()).astype(float)
        viewDir = np.array(c.findtext('viewDir').split()).astype(float)
        viewUp = np.array(c.findtext('viewUp').split()).astype(float)
        if sys.argv[1] == "four-spheres": #projDistance is not included in the four-spheres.xml file
            projDistance=0.85
        else: 
            projDistance = float(c.findtext('projDistance'))
        width = float(c.findtext('viewWidth'))
        height = float(c.findtext('viewHeight'))
        print(viewPoint)
    
    shaderInfo={}
    for c in root.findall("shader"):
        shaderName=c.get("name") #"red", "ball101", ...
        shaderInfo[shaderName]={"diffuseColor":np.array(c.findtext("diffuseColor").split()).astype(float)}
        shaderInfo[shaderName]["specularColor"]=np.array([0,0,0]).astype(float)
        shaderInfo[shaderName]["exponent"]=1.0
        if c.get("type") == "Phong":
            shaderInfo[shaderName]["specularColor"]=np.array(c.findtext("specularColor").split()).astype(float)
            shaderInfo[shaderName]["exponent"]=float(c.findtext("exponent"))
    print("shaderInfo:" ,shaderInfo)
    #shaderInfo: {'blue': {'diffuseColor': array([0.2, 0.3, 0.8]), 'specularColor': array([1., 1., 0.]), 'exponent': '50'}}

    objectInfo={}
    i=1
    for c in root.findall('surface'):   
        type=c.get("type")
        if type == "Sphere":
            center = np.array(c.findtext('center').split()).astype(float)
            radius = float(np.array(c.findtext('radius')))
            shaderRef = c.find("shader").get("ref")
            objectInfo[shaderRef+type+str(i)]={"type":type,"shaderRef":shaderRef,"center":center,"radius":radius}
        elif type == "Box":
            minPt=np.array(c.findtext('minPt').split()).astype(float)
            maxPt=np.array(c.findtext('maxPt').split()).astype(float)
            shaderRef = c.find("shader").get("ref")
            objectInfo[shaderRef+type+str(i)]={"type":type,"shaderRef":shaderRef,"minPt":minPt,"maxPt":maxPt}
        i+=1 #to avoid duplicate names

    print("objectInfo:", objectInfo)    
    #objectInfo: {'redSphere': {'type': 'Sphere', 'shaderRef': 'red', 'center': array([0.   , 1.   , 0.866]), 'radius': 1.0}, 'greenSphe...
    
    lightInfo={}
    i=1
    for c in root.findall('light'):
        light_position = np.array(c.findtext('position').split()).astype(float)
        light_intensity = np.array(c.findtext('intensity').split()).astype(float)
        lightInfo["light"+str(i)]={"lightPosition":light_position,"lightIntensity":light_intensity}
        i+=1
    print("lightInfo: ",lightInfo)
    #lightInfo: {'light1': {'lightPosition': array([-4.,  3.,  5.]), 'lightIntensity': array([0.7, 0.7, 0.7])}}..

    # code.interact(local=dict(globals(), **locals()))

    # Create an empty image
    channels = 3
    img = np.zeros((imgSize[1], imgSize[0], channels), dtype=np.uint8)
    img[:, :] = 0

    w = normalize(-viewDir)
    left = -width / 2
    bottom = -height / 2
    u = normalize(np.cross(viewUp, w))
    v = normalize(np.cross(w, u))

    # Draw the nearest object for each pixel
    for y in np.arange(imgSize[1]):
        for x in np.arange(imgSize[0]):

            k_u = left + width * (x + 0.5) / imgSize[0]
            k_v = bottom + height * (y + 0.5) / imgSize[1]
        
            s = viewPoint + k_u * u + k_v * v - projDistance * w
            ray_p = viewPoint
            ray_d = normalize(s - viewPoint)
            nearest=math.inf
            hitNothing=0

            # find nearest, check hitNothing
            for object in objectInfo:
                if objectInfo[object]["type"]=="Sphere":
                    radius=objectInfo[object]["radius"]
                    center=objectInfo[object]["center"]
                    if rayTrace_Sphere(ray_d,ray_p,radius,center) is None:
                        hitNothing+=1
                    elif rayTrace_Sphere(ray_d,ray_p,radius,center) < nearest:
                        nearest=rayTrace_Sphere(ray_d,ray_p,radius,center)
                        #currentObject=object
                        thisObj = object
                        curObj=shaderInfo[objectInfo[object]["shaderRef"]]
                        #print(currentObject, rayTrace_Sphere(ray_d,ray_p,radius,center))
                elif objectInfo[object]["type"]=="Box":
                    minPt=objectInfo[object]["minPt"]
                    maxPt=objectInfo[object]["maxPt"]
                    if rayTrace_Box(ray_d,ray_p,minPt,maxPt) == None:
                        hitNothing+=1
                    elif rayTrace_Box(ray_d,ray_p,minPt,maxPt) < nearest:
                        nearest = rayTrace_Box(ray_d,ray_p,minPt,maxPt)
                        #currentObject=object
                        thisObj = object
                        curObj=shaderInfo[objectInfo[object]["shaderRef"]]
                        
            # if hitSomething, set curObj to the nearest one

            if hitNothing != len(objectInfo): #hitSomething
                Point=ray_p + ray_d * nearest
                Point = np.array([Point[0], Point[1], Point[2]]).astype(float)
                
                brightness=np.array([.0,.0,.0])
                for light in lightInfo:  #cycle light, for every light
                    #print(light)
                    light_position = lightInfo[light]["lightPosition"]
                    light_intensity = lightInfo[light]["lightIntensity"]
                    lightRay = normalize(light_position - Point)

                    isBlocked = False
                    for otherObject in objectInfo: #check if blocked off from light, by any other object 
                        if otherObject == thisObj:
                            continue
                            
                        if objectInfo[otherObject]["type"]=="Sphere":
                            tempRadius=objectInfo[otherObject]["radius"]
                            tempCenter=objectInfo[otherObject]["center"]
                            if rayTrace_Sphere(lightRay,Point,tempRadius,tempCenter) != None: 
                                isBlocked=True
                                #break
                                
                        elif objectInfo[otherObject]["type"]=="Box":
                            tempMinPt=objectInfo[otherObject]["minPt"]
                            tempMaxPt=objectInfo[otherObject]["maxPt"]
                            if rayTrace_Box(lightRay,Point,tempMinPt,tempMaxPt) != None:
                                isBlocked=True
                                #break
                    
                    if not isBlocked: 
                        normal = None
                        #get normal vec
                        if objectInfo[thisObj]["type"]=="Sphere":
                            center = objectInfo[thisObj]["center"]
                            normal = normalize(Point - center)
                        elif objectInfo[thisObj]["type"]=="Box":
                            minPt=objectInfo[thisObj]["minPt"]
                            maxPt=objectInfo[thisObj]["maxPt"]
                            #doesn't work on some pixels for some reason
                            if np.allclose(Point[0], minPt[0]):
                                normal=np.array([-1,0,0])
                            elif np.allclose(Point[0], maxPt[0]):
                                normal=np.array([1,0,0])
                            elif np.allclose(Point[1], minPt[1]):
                                normal=np.array([0,-1,0])      
                            elif np.allclose(Point[1], maxPt[1]):
                                normal=np.array([0,1,0])
                            elif np.allclose(Point[2], minPt[2]):
                                normal=np.array([0,0,-1])
                            elif np.allclose(Point[2], maxPt[2]):
                                normal=np.array([0,0,1])
                        
                        #print(curObj)
                        diffuseColor_c = curObj["diffuseColor"]
                        specularColor_c=curObj["specularColor"]
                        toEyeRay=normalize(viewPoint-Point)
                        bisector = normalize(lightRay+toEyeRay)
                        exponent=curObj["exponent"]
                        lambertian = diffuseColor_c * light_intensity * max(0, np.dot(lightRay, normal))
                        specular = light_intensity * max(0, np.dot(normal,bisector)**exponent) * specularColor_c
                        brightness += lambertian+specular
                    #else:
                        #print(currentObject,"was blocked from",light,"by",otherObject) bitchiwhichi intersectionpoint radius center diffusecolor intensityLight >> lightray 
            else:
                brightness=np.array([.0,.0,.0])
            
            #print(brightness)
            color = Color(brightness[0],brightness[1],brightness[2])
            color.gammaCorrect(2.2)
            img[imgSize[1] -1 - y][x] = color.toUINT8()


    rawimg = Image.fromarray(img, 'RGB')
    #rawimg.save('out.png')
    rawimg.save(sys.argv[1] + '.png')
    #rawimg.save(scene+"test.png")


if __name__ == "__main__":
    main()
print("end!!!!")
