
from math import sin, cos,pi
import sys
import time
from direct.showbase.ShowBase import ShowBase

from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import *
from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import BitMask32
from panda3d.core import NodePath
from panda3d.core import PandaNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import *
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletHelper
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletHeightfieldShape
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import BulletSoftBodyNode
from panda3d.bullet import BulletSoftBodyConfig
from panda3d.bullet import ZUp
from panda3d.bullet import BulletGhostNode
from direct.interval.IntervalGlobal import *


DEG_TO_RAD = pi / 180  # translates degrees to radians for sin and cos
BULLET_LIFE = 2     # How long bullets stay on screen before removed
BULLET_REPEAT = .2  # How often bullets can be fired
BULLET_SPEED = 10   # Speed bullets move
counter = 0;
health = 100;
tempCount = 0
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                    pos=(0.80,0.93,pos), align=TextNode.ALeft, scale = .05)
def addInstructions1(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                    pos=(0.45,0.93,pos), align=TextNode.ALeft, scale = .05)
def addInstructions2(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                    pos=(0.10,0.93,0.55), align=TextNode.ALeft, scale = .05)

class CharacterController(ShowBase):



    def __init__(self):
        ShowBase.__init__(self)

        self.setupLights()
        fire=1
        # Input
        self.accept('escape', self.doExit)
        #self.accept('r', self.doReset)
        self.accept('f3', self.toggleDebug)
        self.accept('control', self.doJump)
        #self.accept('space', self.fire)
        self.isMoving = False
        inputState.watchWithModifiers('forward', 'arrow_up')
        inputState.watchWithModifiers('reverse', 'arrow_down')
        inputState.watchWithModifiers('turnLeft', 'arrow_left')
        inputState.watchWithModifiers('turnRight', 'arrow_right')
        inputState.watchWithModifiers('topView','w')
        inputState.watchWithModifiers('bottomView','s')
        inputState.watchWithModifiers('leftView','a')
        inputState.watchWithModifiers('rightView','d')
        self.backGroundMusic = base.loader.loadSfx("models/bassRemix.flac")
        self.backGroundMusic.setLoop(True)
        self.backGroundMusic.play()
        self.backGroundMusic.setVolume(0.5)
        # Stores the time at which the next bullet may be fired.
        self.nextBullet = 0.0
        self.myFrame = DirectFrame(frameColor=(0, 0, 0, 1),
                      frameSize=(-1.00, 1.00, 0.90, 1.0 ))


        # self.textObject = OnscreenText(text = "sam", pos = (-1.3,0.95),
        #                   scale = 0.07,fg=(1.3,-0,-0.95,1),align=TextNode.ARight)
        #b = DirectLabel(parent=self.myFrame,text = "OK", scale=.05,pos=(0.5,0.5,0))
       # b.setPos(-1.3,0.95)
        # This list will stored fired bullets.
        self.bullets = []
        self.inst3 = addInstructions(0.85, "Coins: ")
        self.inst4 = addInstructions1(0.55, "Health: 100")
        self.inst5 = addInstructions2(0.55,"Timer: 00:00")
        # Task
        taskMgr.add(self.update, 'updateWorld')

        self.setup()
        base.setBackgroundColor(0.1, 0.1, 0.8, 1)
        base.setFrameRateMeter(True)
        base.disableMouse()
        base.camera.setPos(self.characterNP.getPos())
        base.camera.setHpr(self.characterNP.getHpr())
        base.camera.lookAt(self.characterNP)
        # Create a floater object.  We use the "floater" as a temporary
        # variable in a variety of calculations.
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

    # def incBar(arg):
	#         bar['value'] +=	arg
	#         text = "Progress is:"+str(bar['value'])+'%'
	#         textObject.setText(text)
    #
    # frame = DirectFrame(text = "main", scale = 0.1, pos=(-1,0,1))
    #    # Add button
    # bar = DirectWaitBar(text = "", value = 100, range=100, pos = (0,.4,.4))



    def doExit(self):
        self.cleanup()
        sys.exit(1)

    def doReset(self):
        self.cleanup()
        self.setup()

    def toggleDebug(self):
        if self.debugNP.isHidden():
            self.debugNP.show()
        else:
            self.debugNP.hide()

    def doJump(self):
        self.character.setMaxJumpHeight(5.0)
        self.character.setJumpSpeed(8.0)
        self.jumpSound = base.loader.loadSfx("models/armMoving.ogg")

        self.actorNP.loop("jump")
        #self.actorNP.pose("jump",5)

        self.character.doJump()
        self.jumpSound.setVolume(0.3)
        #self.actorNP.loop("idle")
        self.jumpSound.play()

    # def testAllContactingBodies(self):
    #     # test for all the contacts in the bullet world
    #     manifolds = self.world.getManifolds() # returns a list of BulletPersistentManifold objects
    #     for manifold in manifolds:
    #         if(manifold.getNode0().getName() == "Coin"):
    #             print "Soumk"
            #print manifold.getNode0().getName(), " is in contact with ", manifold.getNode1().getName()

    # def processContacts(self):
    #     # self.testWithEveryBody()
    #     for actorPlayer in self.coins:
    #         self.testWithSingleBody(actorPlayer)

    # def testWithSingleBody(self, secondNode):
    #     # test sphere for contacts with secondNode
    #     contactResult = self.world.contactTestPair(self.characterNP, secondNode) # returns a BulletContactResult object
    #     # for contact in contactResult.getContacts():
    #     #     cp = contact.getManifoldPoint()
    #     #     node0 = contact.getNode0()
    #     #     node1 = contact.getNode1()
    #     #     print node0.getName(), node1.getName(), cp.getLocalPointA()
    #     if len(contactResult.getContacts()) > 0:
    #         print "Sphere is in contact with: ", secondNode.getName()

    def processInput(self, dt):
        speed = Vec3(0, 0, 0)
        omega = 0.0

        if inputState.isSet('forward'):
            speed.setY( 2.0)




        if inputState.isSet('reverse'):
            speed.setY(-2.0)

        if inputState.isSet('left'):    speed.setX(-2.0)
        if inputState.isSet('right'):   speed.setX( 2.0)
        if inputState.isSet('turnLeft'):  omega =  120.0
        if inputState.isSet('turnRight'): omega = -120.0

        if (inputState.isSet('forward')!=0) or (inputState.isSet('reverse')!=0) or (inputState.isSet('left')!=0) or (inputState.isSet('right')!=0):
            if self.isMoving is False:
                self.actorNP.loop("run")
                self.mySound.setVolume(0.3)
                self.mySound.setLoop(True)
                self.mySound.play()
                self.isMoving = True
        else:
            if self.isMoving:
                self.actorNP.stop()
                #self.actorNP.pause("",5)
                self.actorNP.pose("walk",5)
                self.actorNP.loop("walk")
                self.mySound.stop()
                self.isMoving = False


        #self.actorNP.loop('idle')
        self.character.setAngularMovement(omega)
        self.character.setLinearMovement(speed, True)

    # def updateTime(self):
    #     self.myText.setText(str (nowTime))

    def update(self, task):
        dt = globalClock.getDt()
        self.processInput(dt)
        self.world.doPhysics(dt, 4, 1./240.)
        timer = health - dt
        self.inst5.remove_node()
        h = int(round(timer))
        #print h
        nowTime = globalClock.getFrameTime() - self.startTime
        h =  int(round(nowTime))
        self.inst5 = addInstructions2(0.68,' Timer : {}'.format(h))
        if h > 500:
            self.doExit()


        # If the camera is too far from ralph, move it closer.
        # If the camera is too close to ralph, move it farther.
        camvec = self.characterNP.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()

        if (camdist > 15.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-15))
            camdist = 15.0
        if (camdist < 6.0):
            base.camera.setPos(base.camera.getPos() - camvec*(6-camdist))
            camdist = 6.0
        if inputState.isSet('topView'):    base.camera.setZ(base.camera,+20 * globalClock.getDt())
        if inputState.isSet('bottomView'): base.camera.setZ(base.camera, -20 * globalClock.getDt())
        if inputState.isSet('rightView'): base.camera.setX(base.camera, +20 * globalClock.getDt())
        if inputState.isSet('leftView'): base.camera.setX(base.camera, -20 * globalClock.getDt())
        self.floater.setPos(self.characterNP.getPos())
        self.floater.setZ(self.characterNP.getZ() + 0.4)
        base.camera.lookAt(self.floater)
        global tempCount
        if self.characterNP.getZ()<2.50 and tempCount == 0:
            global health
            tempCount= 1

            health = health - 1
            self.inst4.remove()
            self.inst4 = addInstructions1(0.55,"Health: {}".format(health))
            print health
            print self.characterNP.getZ()
        # self.processContacts()
        radius = 0.04

        for coin in render.findAllMatches("**/=coin" ):
            if (self.characterNP.getPos() - coin.getPos()) < radius:
                global counter
                #global addInstructions
                counter = counter + 1
                self.inst3.remove()
                self.inst3 = addInstructions(0.68, "Coins:{} ".format(counter))

                # b = OnscreenText(parent=self.myFrame , scale=0.1, pos=(0.80,0.93,0.68),fg=(0.8,0.6,0.5,1))
                # # if counter!=1:
                # #     b.destroy()
                # #     #b.destroy()
                # b = OnscreenText(parent=self.myFrame , scale=0.1, pos=(0.80,0.93,0.68),fg=(0.8,0.6,0.5,1))
                #
                # b.setText('Coins: {}'.format(counter))

                #b.setPos(-1.3,0.95)

                print counter
                coin.removeNode()
                #b.destroy()


#        self.testAllContactingBodies()
        return task.cont

    def cleanup(self):
        self.world = None
        self.render.removeNode()

    def setupLights(self):
        # Light
        alight = AmbientLight('ambientLight')
        alight.setColor(Vec4(0.5, 0.5, 0.5, 1))
        alightNP = render.attachNewNode(alight)

        dlight = DirectionalLight('directionalLight')
        dlight.setDirection(Vec3(1, 1, -1))
        dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
        dlightNP = render.attachNewNode(dlight)

        self.render.clearLight()
        self.render.setLight(alightNP)
        self.render.setLight(dlightNP)

    def setup(self):

        # World

        self.debugNP = self.render.attachNewNode(BulletDebugNode('Debug'))
        self.debugNP.show()

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        self.world.setDebugNode(self.debugNP.node())
        self.startTime = globalClock.getFrameTime()

        # Floor
        shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        floorNP = self.render.attachNewNode(BulletRigidBodyNode('Floor'))
        floorNP.node().addShape(shape)
        floorNP.setPos(0, 0, 0)
        #floorNP.setCollideMask(BitMask32.allOn())
        self.world.attachRigidBody(floorNP.node())

        self.environ = loader.loadModel("models/environment")
        self.environ.reparentTo(floorNP)
        self.grass = loader.loadTexture("models/grass.jpg")
        self.environ.setTexture(self.grass, 1)
        # Stair
        origin = Point3(2, 0, 0)
        size = Vec3(4, 4.75, 1.0)
        #ballSize= Vec3(4.75,5.75,2.75)
        height = 0
        angle = -25


        for i in range(10):
            shape = BulletBoxShape(size * 0.55)
            pos = origin * i + size * i
            pos.setY(0)
            pos.setX(pos.getX()*1)
            stairNP = self.render.attachNewNode(BulletRigidBodyNode('Stair%i' % i))
            stairNP.node().addShape(shape)
            stairNP.setPos(pos)
            stairNP.setCollideMask(BitMask32.allOn())

            if i % 2 == 0:
                #print "soiumik"
                stairHprInterval1 = stairNP.hprInterval(4, Point3(pos),
                                                                            startHpr=Point3(360, 0, 0))
                stairHprInterval = stairNP.hprInterval(4, Point3(pos),
                                                            startHpr=Point3(360, 0, 0))
                self.actorRobot = Sequence(stairHprInterval,stairHprInterval1)
                self.actorRobot.loop()
            modelNP = loader.loadModel('models/box.egg')
            modelNP.reparentTo(stairNP)
            modelNP.setPos(-size.x/2.0, -size.y/2.0, -size.z/2.0)
            modelNP.setScale(size)
            self.world.attachRigidBody(stairNP.node())


        for i in range(10):
            shape = BulletBoxShape(size * 0.55)
            pos = origin * i + size * i
            #ballPos = origin * i + 1 + size * i +2
            pos.setY(0)
            pos.setX(pos.getX()*-1)
            #print actorNP.getZ()
            if i % 2 == 0:
                #print "soiumik"
                stairHprInterval1 = stairNP.hprInterval(3, Point3(),
                                                                            startHpr=Point3(360, 0, 0))
                stairHprInterval = stairNP.hprInterval(3, Point3(pos),
                                                            startHpr=Point3(360, 0, 0))
                self.actorRobot = Sequence(stairHprInterval,stairHprInterval1)
                self.actorRobot.loop()
            stairNP = self.render.attachNewNode(BulletRigidBodyNode('Stair%i' % i))
            stairNP.node().addShape(shape)
            stairNP.setPos(pos)
            stairNP.setCollideMask(BitMask32.allOn())
            if i % 2 == 0:
                coinModel = loader.loadModel('models/coin')
                coinModel.reparentTo(self.render)
                coinModel.setPos(pos+1)
#               coinModel.setZ(1.0)
                coinModel.setScale(0.5)
                coinModel.setHpr(0,0,90)
                coinModel.setTag("coin",str(i))
                self.moon_tex = loader.loadTexture("models/gold.jpg")
    	        coinModel.setTexture(self.moon_tex, 1)
            modelNP = loader.loadModel('models/box.egg')
            modelNP.reparentTo(stairNP)
            modelNP.setPos(-size.x/2.0, -size.y/2.0, -size.z/2.0)
            modelNP.setScale(size)
            self.world.attachRigidBody(stairNP.node())


        # Character
        h = 4.75
        w = 0.5
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)
        self.character = BulletCharacterControllerNode(shape, 0.4, 'Player')
        #    self.character.setMass(1.0)
        self.characterNP = self.render.attachNewNode(self.character)
        self.characterNP.setPos(-2, 0, 14)
        self.characterNP.setH(45)
        self.characterNP.setCollideMask(BitMask32.allOn())
        self.world.attachCharacter(self.character)

        self.actorNP = Actor('models/robot/lack.egg', {
                         'run' : 'models/robot/lack-run.egg',
                         'walk' : 'models/robot/lack-idle.egg',
                         'jump' : 'models/robot/lack-jump.egg'})

        self.mySound = base.loader.loadSfx("models/walk.ogg")
        self.jumpSound = base.loader.loadSfx("models/armMoving.ogg")



        self.actorNP.reparentTo(self.characterNP)
        self.actorNP.setScale(0.2048)
        self.actorNP.setH(180)
        self.actorNP.setPos(0, 0, 0)





        # Creates a bullet and adds it to the bullet list
    def fire(self, time):

        dt = globalClock.getDt()
        if task.time > self.nextBullet:
            self.fire(task.time)  # If so, call the fire function
        # And disable firing for a bit
            self.nextBullet = task.time + BULLET_REPEAT
        # Remove the fire flag until the next spacebar press
            fire = 0
        #self.keys["fire"] = 0
            direction = DEG_TO_RAD * self.ship.getR()
            pos = self.ship.getPos()
            bullet = loadObject("bullet.png", scale=.2)  # Create the object
            bullet.setPos(pos)
        # Velcity is in relation to the ship
            vel =(self.getVelocity(self.actorNP) +
                    (LVector3(sin(direction), 0, cos(direction)) *
                    BULLET_SPEED))
            self.setVelocity(bullet, vel)
            # Set the bullet expiration time to be a certain amount past the
            # current time
            self.setExpires(bullet, time + BULLET_LIFE)

            # Finally, add the new bullet to the list
            self.bullets.append(bullet)


game = CharacterController()
game.run()
