from math import sin, cos,pi
import sys
import time
from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import TransparencyAttrib
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
from direct.interval.LerpInterval import LerpPosInterval
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
enemiess = 7;
counterBullet = 0;
tempCount = 0
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                    pos=(-0.02,0.93,pos), align=TextNode.ALeft, scale = .05)
def addInstructions1(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                    pos=(0.65,0.93,pos), align=TextNode.ALeft, scale = .05)
def addInstructions2(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                    pos=(0.35,0.93,0.55), align=TextNode.ALeft, scale = .05)
def storyModeConversation(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                    pos=(-0.90,-0.97,0), align=TextNode.ALeft, scale = .05)
def gameOverText(pos, msg):
    return OnscreenText(text=msg, style=2, fg=(1,1,1,1),
                    pos=(-1.0,0,0), align=TextNode.ALeft, scale = 0.10)
# def enemyNumber(pos, msg):
#     return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
#                     pos=(0.10,0.93,0.55), align=TextNode.ALeft, scale = .05)

class CharacterController(ShowBase):



    def __init__(self):
        ShowBase.__init__(self)
        self.bombs = []
        self.keys = {"fire":0}
        self.setupLights()
        fire=1

        self.bullet=[]
        self.enemy1Bullet = []
        # Input
        self.accept('escape', self.doExit)
        #self.accept('r', self.doReset)
        self.accept('f3', self.toggleDebug)
        self.accept('control', self.doJump)
        self.accept('space',self.fire)
        self.accept('b',self.secondaryFire)
        self.accept('enter',self.startGame)
        #self.accept('fire','space')
        self.isMoving = False
        self.isEnemyFire = False
        #inputState.watchWithModifiers('fire','space')
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
        self.storyMode = DirectFrame(frameColor=(0,0,0,1),
                        frameSize=(1.00,-1.00,-1.0,-0.9),pos=(0,-3,0))



        # self.textObject = OnscreenText(text = "sam", pos = (-1.3,0.95),
        #                   scale = 0.07,fg=(1.3,-0,-0.95,1),align=TextNode.ARight)
        #b = DirectLabel(parent=self.myFrame,text = "OK", scale=.05,pos=(0.5,0.5,0))
       # b.setPos(-1.3,0.95)
        # This list will stored fired bullets.
        self.bullets = []
        self.isFire = False
        self.inst3 = addInstructions(0.65, "Enemies left: 7 ")
        self.inst4 = addInstructions1(0.55, "Health: 100")
        self.inst5 = addInstructions2(0.55,"Timer: 00:00")
        self.story = storyModeConversation(0.10,"Hello, There are 4 enemies on ground and 3 on planks. Kill them'll")
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

        self.actorNP.play("jump")
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
                #self.actorNP.play('attack')
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
        global health
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
        # if (camdist < 5.0):
        #     base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
        #     camdist = 5.0
        if inputState.isSet('topView'):    base.camera.setZ(base.camera,+20 * globalClock.getDt())
        if inputState.isSet('bottomView'): base.camera.setZ(base.camera, -20 * globalClock.getDt())
        if inputState.isSet('rightView'): base.camera.setX(base.camera, +20 * globalClock.getDt())
        if inputState.isSet('leftView'): base.camera.setX(base.camera, -20 * globalClock.getDt())
        self.floater.setPos(self.characterNP.getPos())
        self.floater.setZ(self.characterNP.getZ() + 0.4)
        base.camera.lookAt(self.floater)
        global tempCount
        if self.characterNP.getZ()>4.33:
            #print self.characterNP.getZ()
            tempCount = 0
        if self.characterNP.getZ()<2.50 and tempCount == 0:

            tempCount= 1

            health = health - 5
            self.inst4.remove_node()
            self.inst4 = addInstructions1(0.55,"Health: {}".format(health))
            print health
            print self.characterNP.getZ()
        # self.processContacts()
        radius = 0.05
        global enemiess
        global counterBullet
        enemy0 = self.beefyManNP.getPos()
        enemy1 = self.beefyManNP1.getPos()
        enemy2 = self.beefyManNP2.getPos()
        enemy3 = self.beefyManNP3.getPos()
        enemy5 = self.beefyManNP5.getPos()
        enemy6 = self.beefyManNP6.getPos()
        enemy7 = self.beefyManNP7.getPos()
        master = self.masterNP.getPos()
        evil = self.evilNP.getPos()
        actor = self.characterNP.getPos()

        distance1 = actor - enemy0
        distance2 = actor - enemy1
        distance3 = actor -enemy2
        distance4 = actor - enemy3
        distance5 = actor - enemy5
        distance6 = actor - enemy6
        distance7 = actor - enemy7
        distance8 = actor - master
        distance9 = actor - evil

        # distance1.setZ(0)
        # distance2.setZ(0)
        # distance3.setZ(0)
        # distance4.setZ(0)
        # distance5.setZ(0)
        # distance6.setZ(0)
        # distance7.setZ(0)
        # distance8.setZ(0)
        # distance9.setZ(0)

        enemyDist = distance1.length()
        enemyDist1 = distance2.length()
        enemyDist2 = distance3.length()
        enemyDist3 = distance4.length()
        enemyDist4 = distance5.length()
        enemyDist5 = distance6.length()
        enemyDist6 = distance7.length()
        enemyDist7 = distance8.length()
        enemyDist8 = distance9.length()

        #print "this is enemy distance",enemyDist1
        #global isFire

####################################################################### Enemy 1             ###########################################################################
        if enemyDist < 15 :
            self.story.destroy()
            self.story = storyModeConversation(0.10,"First Enemy: Do you hear something?")
            #counterBullet = 0


            if enemyDist < 10 and counterBullet == 0:
                self.beefyManNP.lookAt(self.characterNP.getPos())
                self.beefyManNP.setH(self.beefyManNP.getH()+180)
                counterBullet =1

                self.enemyFire(self.beefyManNP)
                self.isEnemyFire = False
                health = health - 5
                self.inst4.remove_node()
                self.inst4 = addInstructions1(0.55,"Health: {}".format(health))

            if enemyDist < 6 and self.isFire == True:
                #self.actorNP.setPos(self.beefyManNP.getPos()+distance1*(3-enemyDist))

                self.beefyManNP.hide()
                self.story.destroy()
                counterBullet = 0
                self.isFire = False
                if self.beefyManNP.hide() is True:
                    print "gela re.."
                    enemiess = enemiess - 1
                    self.inst3.destroy()
                    self.inst3 = addInstructions(0.65, "Enemies left:  "+str(enemiess))

            if enemyDist < 2 :
                self.characterNP.setPos(self.characterNP.getPos()-enemyDist+1)
##############################################################################     Enemy 2 ##########################################################################
        if enemyDist1 < 15:
            self.story.destroy()
            self.story = storyModeConversation(0.10,"Second Enemy: Don't move, I hear something..")

            if enemyDist1 < 10 and counterBullet == 0:
                self.beefyManNP1.lookAt(self.characterNP.getPos())
                self.beefyManNP1.setH(self.beefyManNP1.getH()+180)
                counterBullet = 1
                self.enemyFire(self.beefyManNP1)
                health = health - 5
                self.inst4.remove_node()
                self.inst4 = addInstructions1(0.55,"Health: {}".format(health))
            if enemyDist1 < 6 and self.isFire == True:
                self.beefyManNP1.hide()
                self.story.destroy()
                enemiess = enemiess - 1
                self.inst3.destroy()
                counterBullet = 0
                self.inst3 = addInstructions(0.65, "Enemies left:  "+str(enemiess))
                self.isFire = False
            if enemyDist1 < 2 :
                self.characterNP.setPos(self.characterNP.getPos()-enemyDist1+1)

#############################################################################           ENEMY 3 ######################################################################
        if enemyDist2 < 15 :
            self.story.destroy()
            self.story = storyModeConversation(0.10,"Third Enemy: who's there? come out or I'll fire.....*HEY*")
            if enemyDist2 < 10 and counterBullet == 0:
                self.beefyManNP2.lookAt(self.characterNP.getPos())
                self.beefyManNP2.setH(self.beefyManNP2.getH()+180)
                counterBullet = 1
                self.enemyFire(self.beefyManNP2)
                health = health - 5
                self.inst4.remove_node()
                self.inst4 = addInstructions1(0.55,"Health: {}".format(health))
                self.isEnemyFire = False
            if enemyDist2 < 6 and self.isFire == True:
                self.beefyManNP2.hide()
                self.story.destroy()
                enemiess = enemiess - 1
                counterBullet = 0
                self.inst3.destroy()
                self.inst3 = addInstructions(0.65, "Enemies left:  "+str(enemiess))
                self.isFire = False
            if enemyDist2 < 2 :
                self.characterNP.setPos(self.characterNP.getPos()-enemyDist2+1)
###################################################################         ENEMY 4     ############################################################################
        if enemyDist3 <15:
            self.story.destroy()
            self.story = storyModeConversation(0.10,"Forth Enemy: Do you hear something? Srgt Thomas come in..anybody listening?")
            if enemyDist3 < 10 and counterBullet == 0:
                self.beefyManNP3.lookAt(self.characterNP.getPos())
                self.beefyManNP3.setH(self.beefyManNP3.getH()+180)
                counterBullet =1
                self.enemyFire(self.beefyManNP3)
                health = health - 5
                self.inst4.remove_node()
                self.inst4 = addInstructions1(0.55,"Health: {}".format(health))

                self.isEnemyFire = False
            if enemyDist3 < 6 and self.isFire == True:
                self.beefyManNP3.hide()
                self.story.destroy()
                enemiess = enemiess - 1
                self.inst3.destroy()
                counterBullet = 0
                self.inst3 = addInstructions(0.65, "Enemies left:  "+str(enemiess))
                self.isFire = False
            if enemyDist3 < 2 :
                self.characterNP.setPos(self.characterNP.getPos()-enemyDist3+1)
#################################################################           ENEMY 5         ##########################################################################
        if enemyDist4 <15:
            self.story.destroy()
            self.story = storyModeConversation(0.10,"Fifth Enemy: We got company, take cover..take cover")
            self.beefyManNP5.lookAt(self.characterNP.getPos())
            self.beefyManNP5.setH(self.beefyManNP5.getH()+180)
            if enemyDist4 < 10 and counterBullet == 0:
                self.beefyManNP5.lookAt(self.characterNP.getPos())
                self.beefyManNP5.setH(self.beefyManNP5.getH()+180)
                counterBullet =1
                self.enemyFire(self.beefyManNP5)
                health = health - 5
                self.inst4.remove_node()
                self.inst4 = addInstructions1(0.55,"Health: {}".format(health))
            if enemyDist4 < 6 and self.isFire == True:
                self.beefyManNP5.hide()
                self.story.destroy()
                counterBullet = 0
                enemiess = enemiess - 1
                self.inst3.destroy()
                self.inst3 = addInstructions(0.65, "Enemies left:  "+str(enemiess))
                self.isFire = False
            if enemyDist4 < 2 :
                self.characterNP.setPos(self.characterNP.getPos()-enemyDist4+1)
############################################################        ENEMY 6         ##################################################################################
            #self.beefyManNP5.loop('idle')
        if enemyDist5 <15:
            self.story.destroy()
            self.story = storyModeConversation(0.10,"Sixth Enemy: I got this..")
            if enemyDist5 < 10 and counterBullet == 0:
                self.beefyManNP6.lookAt(self.characterNP.getPos())
                self.beefyManNP6.setH(self.beefyManNP6.getH()+180)
                counterBullet =1
                self.enemyFire(self.beefyManNP6)
                health = health - 5
                self.inst4.remove_node()
                self.inst4 = addInstructions1(0.55,"Health: {}".format(health))
            if enemyDist5 < 6 and self.isFire == True:
                self.beefyManNP6.hide()
                counterBullet = 0
                self.story.destroy()
                enemiess = enemiess - 1
                self.inst3.destroy()
                self.inst3 = addInstructions(0.65, "Enemies left:  "+str(enemiess))
                self.isFire =False
            if enemyDist5 < 2 :
                self.characterNP.setPos(self.characterNP.getPos()-enemyDist5+1)
#####################################################################       ENEMY 7         #######################################################################
        if enemyDist6 < 15:
            self.story.destroy()
            self.story = storyModeConversation(0.10,"Master: I knew he would come, I had faith in my creation")
            if enemyDist6 < 10 and counterBullet == 0:
                self.beefyManNP7.lookAt(self.characterNP.getPos())
                self.beefyManNP7.setH(self.beefyManNP7.getH()+180)
                counterBullet =1
                self.enemyFire(self.beefyManNP7)
                health = health - 5
                self.inst4.remove_node()
                self.inst4 = addInstructions1(0.55,"Health: {}".format(health))
            if enemyDist6 < 6 and self.isFire == True:
                self.beefyManNP7.hide()
                self.story.destroy()
                counterBullet = 0
                enemiess = enemiess - 1
                self.inst3.destroy()
                self.inst3 = addInstructions(0.65, "Enemies left:  "+str(enemiess))
                self.isFire = False

###########################################################################         MASTER              ##############################################################
        if enemyDist8 < 15:
            self.story.destroy()
            self.story = storyModeConversation(0.10,"I'll explode this iron tin")
            if enemyDist8 < 10 and counterBullet == 0:
                self.evilNP.lookAt(self.characterNP.getPos())
                self.evilNP.setH(self.evilNP.getH()+180)
                counterBullet =1
                self.enemyFire(self.evilNP)
                health = health - 15
                self.inst4.remove_node()
                self.inst4 = addInstructions1(0.55,"Health: {}".format(health))
            if enemyDist8 < 6 and self.isFire == True:
                self.evilNP.hide()
                self.story.destroy()
                counterBullet = 0
                enemiess = enemiess - 1
                self.inst3.destroy()
                self.inst3 = addInstructions(0.65, "Enemies left:  "+str(enemiess))
                self.isFire = False
            if enemyDist8 < 2 :
                self.characterNP.setPos(self.characterNP.getPos()-enemyDist8+1)



        for coin in render.findAllMatches("**/=coin" ):
            distOfPlayer = self.characterNP.getPos() - coin.getPos()
            if  (self.characterNP.getPos() - coin.getPos())< radius:
                #global counter
                #global addInstructions
                global health
                #tempCount= 1
                if health < 100:
                    health = health + 5
                    self.story.destroy()
                    self.story = storyModeConversation(0.10,"You Just received 5 health")
                    coin.removeNode()

                elif health == 100:
                    health = health
                self.inst4.remove_node()
                self.inst4 = addInstructions1(0.55,"Health: {}".format(health))

        for bomb in self.bombs:
            timeAsString  = bomb.getTag("timer")
            #print type(timeAsString), timeAsString
            timeSinceBombWasCreated = globalClock.getRealTime() - float(timeAsString)
            #print "Time Diff: ", timeSinceBombWasCreated
            if timeSinceBombWasCreated > 3.0:
            #    print "Removing Node"
                bomb.removeNode()
                self.bombs.remove(bomb)
        for bomb in self.enemy1Bullet:
            timeAsString  = bomb.getTag("timerForEnemy")
            #print type(timeAsString), timeAsString
            timeSinceBombWasCreated = globalClock.getRealTime() - float(timeAsString)
            #print "Time Diff: ", timeSinceBombWasCreated
            if timeSinceBombWasCreated > 3.0:
                #print "Removing Node"
                bomb.removeNode()
                self.enemy1Bullet.remove(bomb)

        if health == 0:
            taskMgr.remove('updateWorld')
            self.inst6 = gameOverText(0,'Game Over, Press Enter to play again')

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

            if i % 3 == 0:
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
                # coinHprInterval = coinModel.hprInterval(3, Point3(), startHpr = Point3(360,0,0))
                # coinHprInterval1 = coinModel.hprInterval(3, Point3(), startHpr = Point3(360,0,0))
                #
                # self.coinRotate = Sequence(coinHprInterval,coinHprInterval1)
                # self.coinRotate.loop()
                coinModel.setTag("coin",str(i))
                self.moon_tex = loader.loadTexture("models/gold.jpg")
    	        coinModel.setTexture(self.moon_tex, 1)
            modelNP = loader.loadModel('models/box.egg')
            modelNP.reparentTo(stairNP)
            modelNP.setPos(-size.x/2.0, -size.y/2.0, -size.z /2.0)
            modelNP.setScale(size)
            self.world.attachRigidBody(stairNP.node())

        origin1 = Point3(-70,3,8.50)
        plank = BulletBoxShape(Vec3(6, 9.75, 0.5))
        plankNP = self.render.attachNewNode(BulletRigidBodyNode('PLANK'))
        plankNP.setCollideMask(BitMask32.allOn())
        plankNP.node().addShape(plank)
        plankNP.setPos(-60, 0, 9)
        #print pos.getX(),'sadsa',pos.getY(),"Z",pos.getZ()
        self.stoner = loader.loadModel("models/stone")
        self.stoner.reparentTo(plankNP)
        self.stoner.setPos(0,0,0) #pos.getX()-6,pos.getY(),pos.getZ()-1
        self.stoner.setScale(13 ,20 , 0)
        self.world.attachRigidBody(plankNP.node())

        plank = BulletBoxShape(Vec3(6, 9.75, 0.5))
        plankNP = self.render.attachNewNode(BulletRigidBodyNode('PLANK'))
        plankNP.setCollideMask(BitMask32.allOn())
        plankNP.node().addShape(plank)
        plankNP.setPos(-65, 21, 9)
        #print pos.getX(),'sadsa',pos.getY(),"Z",pos.getZ()
        self.stoner = loader.loadModel("models/stone")
        self.stoner.reparentTo(plankNP)
        self.stoner.setPos(0,0,0) #pos.getX()-6,pos.getY(),pos.getZ()-1
        self.stoner.setScale(13 ,20 , 0)
        self.world.attachRigidBody(plankNP.node())


        for i in range(10):
            #print i
            shape = BulletBoxShape(size * 0.55)
            pos = origin1  + size * -i
            pos.setY(0)
            pos.setX(pos.getX()*1)

            if i % 2 == 0:
                #print "soiumik"
                stairPosInterval1 = stairNP.posInterval(8, Point3(stairNP.getX(),stairNP.getY()+4,stairNP.getZ()),
                                                                            startPos=Point3(stairNP.getX(),stairNP.getY()-4,stairNP.getZ()))
                stairPosInterval = stairNP.posInterval(8, Point3(stairNP.getX(),stairNP.getY()-4,stairNP.getZ()),
                                                            startPos=Point3(stairNP.getX(),stairNP.getY()+4,stairNP.getZ()))
                self.actorStair = Sequence(stairPosInterval1,stairPosInterval)
                self.actorStair.loop()
            stairNP = self.render.attachNewNode(BulletRigidBodyNode('Stair%i' % i))
            stairNP.node().addShape(shape)
            stairNP.setPos(pos)
            #print stairNP.getX(),' X, Y :',stairNP.getY(),' Z: ',stairNP.getZ()
            #stairNP.setHpr(360,0,0)
            stairNP.setCollideMask(BitMask32.allOn())
            modelNP = loader.loadModel('models/box.egg')
            modelNP.reparentTo(stairNP)
            modelNP.setPos(-size.x/2.0, -size.y/2.0, -size.z/3.0)
            modelNP.setScale(size)
            self.world.attachRigidBody(stairNP.node())





############################################################################################################
        # Character
        h = 4.95
        w = 0.5
        shape = BulletCapsuleShape(w, h - 2 * w, ZUp)
        self.character = BulletCharacterControllerNode(shape, 0.4, 'Player')
        #    self.character.setMass(1.0)
        self.characterNP = self.render.attachNewNode(self.character)
        self.characterNP.setPos(-2, 0, 14)
        # self.characterNP.setH(45)
        self.characterNP.setCollideMask(BitMask32.allOn())
        self.world.attachCharacter(self.character)

        self.actorNP = Actor('models/robot/lack.egg', {
                         'run' : 'models/robot/lack-run.egg',
                         'walk' : 'models/robot/lack-idle.egg',
                         'jump' : 'models/robot/lack-jump.egg',
                         'attack': 'models/robot/lack-damage.egg'})

        self.mySound = base.loader.loadSfx("models/walk.ogg")
        self.jumpSound = base.loader.loadSfx("models/armMoving.ogg")



        self.actorNP.reparentTo(self.characterNP)
        self.actorNP.setScale(0.2048)
        self.actorNP.setH(180)
        self.actorNP.setPos(0, 0, 0)

        # slight = Spotlight('slight')
        # slight.setColor(VBase4(0, 1, 1, 1))
        # lens = PerspectiveLens()
        # slight.setLens(lens)
        # slnp = render.attachNewNode(slight)
        # slnp.setPos(10, 20, 0)
        # slnp.lookAt(self.characterNP.getPos())
        # render.setLight(slnp)


    # shape = BulletCapsuleShape(w, h - 2 * w, ZUp)
    # self.character = BulletCharacterControllerNode(shape, 0.4, 'Player')
    # #    self.character.setMass(1.0)
    # self.characterNP = self.render.attachNewNode(self.character)
    # self.characterNP.setPos(-2, 0, 14)
    # self.characterNP.setH(45)
    # self.characterNP.setCollideMask(BitMask32.allOn())
    # self.world.attachCharacter(self.character)
#########################################             ENEMY 1           ########################################################################

        # beefShape = BulletCapsuleShape(w+0.10,h-3 *w,ZUp)
        # self.beefyCharacter = BulletCharacterControllerNode(beefShape,0.4,'enemy')
        # self.beefyCharacterNP = self.render.attachNewNode(self.beefyCharacter)
        # #self.beefyCharacterNP.node().addShape(beefShape)
        #
        # self.beefyCharacterNP.setPos(-5,20,2)
        # self.beefyCharacterNP.setH(90)
        # self.beefyCharacterNP.setCollideMask(BitMask32.allOn())
        # self.world.attachCharacter(self.beefyCharacter)

        self.beefyManNP = Actor('models/beefy/beefy.egg',{
                                'walk':'models/beefy/beefy-walk.egg',
                                'idle':'models/beefy/beefy-idle.egg'})
        self.beefyManNP.reparentTo(render)
        self.beefyManNP.setScale(0.2)
        self.beefyManNP.setH(90)
        self.beefyManNP.setPos(-5,20,2)

        enemyPosInterval1 = self.beefyManNP.posInterval(13, Point3(self.beefyManNP.getX()+4,self.beefyManNP.getY(),self.beefyManNP.getZ()),
                                                            startPos=Point3(self.beefyManNP.getX()-4,self.beefyManNP.getY(),self.beefyManNP.getZ()))
        enemyPosInterval2 = self.beefyManNP.posInterval(13, Point3(self.beefyManNP.getX()-4,self.beefyManNP.getY(),self.beefyManNP.getZ()),
                                                            startPos=Point3(self.beefyManNP.getX()+4,self.beefyManNP.getY(),self.beefyManNP.getZ()))
        enemyHprInterval1 = self.beefyManNP.hprInterval(3, Point3(self.beefyManNP.getH()+180,self.beefyManNP.getP(),self.beefyManNP.getR()),
                                                            startHpr=Point3(0, 0, 0))
        enemyHprInterval2 = self.beefyManNP.hprInterval(3, Point3(0, 0, 0),
                                                            startHpr=Point3(self.beefyManNP.getH()+180, self.beefyManNP.getP(),self.beefyManNP.getR()))
        self.enemyPace = Sequence(enemyPosInterval1,enemyHprInterval1,
                                      enemyPosInterval2, enemyHprInterval2)
        self.enemyPace.loop()
        self.beefyManNP.loop('walk')
##############################################          ENEMY 2                     ######################################################################
#         beefShape = BulletCapsuleShape(w+0.10,h-3 *w,ZUp)
#         #self.beefyCharacter1 = BulletCharacterControllerNode(beefShape,0.4,'enemy')
#         self.beefyCharacterNP1 = self.render.attachNewNode(BulletRigidBodyNode('enemy1'))
#         self.beefyCharacterNP1.node().addShape(beefShape)
#         self.beefyCharacterNP1.setPos(-10,15,2)
#         self.beefyCharacterNP1.setH(90)
# #        self.beefyCharacterNP1.setCollideMask(BitMask32.allOn())
#         self.world.attachRigidBody(self.beefyCharacterNP1.node())

        self.beefyManNP1 = Actor('models/beefy/beefy.egg',{
                                'walk':'models/beefy/beefy-walk.egg',
                                'idle':'models/beefy/beefy-idle.egg'})
        self.beefyManNP1.reparentTo(render)
        self.beefyManNP1.setScale(0.2)
#        self.beefyManNP1.setH(180)
        self.beefyManNP1.setPos(10,15,2)
        enemy1PosInterval1 = self.beefyManNP1.posInterval(13, Point3(self.beefyManNP1.getX(),self.beefyManNP1.getY()+4,self.beefyManNP1.getZ()),
                                                            startPos=Point3(self.beefyManNP1.getX(),self.beefyManNP1.getY()-4,self.beefyManNP1.getZ()))
        enemy1PosInterval2 = self.beefyManNP1.posInterval(13, Point3(self.beefyManNP1.getX(),self.beefyManNP1.getY()-4,self.beefyManNP1.getZ()),
                                                            startPos=Point3(self.beefyManNP1.getX(),self.beefyManNP1.getY()+4,self.beefyManNP1.getZ()))
        enemy1HprInterval1 = self.beefyManNP1.hprInterval(3, Point3(self.beefyManNP1.getH()+180,self.beefyManNP1.getP(),self.beefyManNP1.getR()),
                                                            startHpr=Point3(0, 0, 0))
        enemy1HprInterval2 = self.beefyManNP1.hprInterval(3, Point3(0, 0, 0),
                                                            startHpr=Point3(self.beefyManNP1.getH()+180, self.beefyManNP1.getP(),self.beefyManNP1.getR()))
        self.enemy1Pace = Sequence(enemy1PosInterval2,enemy1HprInterval1,
                                      enemy1PosInterval1, enemy1HprInterval2)
        self.enemy1Pace.loop()

        self.beefyManNP1.loop('walk')

########################################################          ENEMY 3               ####################################################################
#         beefShape = BulletCapsuleShape(w+0.10,h-3*w,ZUp)
#         self.beefyCharacterNP2 = self.render.attachNewNode(BulletRigidBodyNode('enemy2'))
#         self.beefyCharacterNP2.node().addShape(beefShape)
#         self.beefyCharacterNP2.setPos(-10,-20,2)
#         self.beefyCharacterNP2.setH(0)
# #        self.beefyCharacterNP1.setCollideMask(BitMask32.allOn())
#         self.world.attachRigidBody(self.beefyCharacterNP2.node())

        self.beefyManNP2 = Actor('models/beefy/beefy.egg',{
                                'walk':'models/beefy/beefy-walk.egg',
                                'idle':'models/beefy/beefy-idle.egg'})
        self.beefyManNP2.reparentTo(render)
        self.beefyManNP2.setScale(0.2)
        self.beefyManNP2.setH(0)
        self.beefyManNP2.setPos(-10,-20,2)
        enemy2PosInterval1 = self.beefyManNP2.posInterval(13, Point3(self.beefyManNP2.getX(),self.beefyManNP2.getY()+4,self.beefyManNP2.getZ()),
                                                            startPos=Point3(self.beefyManNP2.getX(),self.beefyManNP2.getY()-4,self.beefyManNP2.getZ()))
        enemy2PosInterval2 = self.beefyManNP2.posInterval(13, Point3(self.beefyManNP2.getX(),self.beefyManNP2.getY()-4,self.beefyManNP2.getZ()),
                                                            startPos=Point3(self.beefyManNP2.getX(),self.beefyManNP2.getY()+4,self.beefyManNP2.getZ()))
        enemy2HprInterval1 = self.beefyManNP2.hprInterval(3, Point3(self.beefyManNP2.getH()+180,self.beefyManNP2.getP(),self.beefyManNP2.getR()),
                                                            startHpr=Point3(0, 0, 0))
        enemy2HprInterval2 = self.beefyManNP2.hprInterval(3, Point3(0, 0, 0),
                                                            startHpr=Point3(self.beefyManNP2.getH()+180, self.beefyManNP2.getP(),self.beefyManNP2.getR()))
        self.enemy2Pace = Sequence(enemy2PosInterval2,enemy2HprInterval1,
                                      enemy2PosInterval1, enemy2HprInterval2)
        self.enemy2Pace.loop()
        self.beefyManNP2.loop('walk')

####################################################                ENEMY 4                  ########################################################################
        # beefShape = BulletCapsuleShape(w+0.10,h-3*w,ZUp)
        # self.beefyCharacterNP3 = self.render.attachNewNode(BulletRigidBodyNode('enemy3'))
        # self.beefyCharacterNP3.node().addShape(beefShape)
        # self.beefyCharacterNP3.setPos(-5,-15,2)
        # self.beefyCharacterNP3.setH(90)
#        self.beefyCharacterNP1.setCollideMask(BitMask32.allOn())
        #self.world.attachRigidBody(self.beefyCharacterNP3.node())
        self.beefyManNP3 = Actor('models/beefy/beefy.egg',{
                                'walk':'models/beefy/beefy-walk.egg',
                                'idle':'models/beefy/beefy-idle.egg'})
        self.beefyManNP3.reparentTo(render)
        self.beefyManNP3.setScale(0.2)
        self.beefyManNP3.setH(90)
        self.beefyManNP3.setPos(15,-15,2)
        enemy3PosInterval1 = self.beefyManNP3.posInterval(13, Point3(self.beefyManNP3.getX()-4,self.beefyManNP3.getY(),self.beefyManNP3.getZ()),
                                                            startPos=Point3(self.beefyManNP3.getX()+4,self.beefyManNP3.getY(),self.beefyManNP3.getZ()))
        enemy3PosInterval2 = self.beefyManNP3.posInterval(13, Point3(self.beefyManNP3.getX()+4,self.beefyManNP3.getY(),self.beefyManNP3.getZ()),
                                                            startPos=Point3(self.beefyManNP3.getX()-4,self.beefyManNP3.getY(),self.beefyManNP3.getZ()))
        enemy3HprInterval1 = self.beefyManNP3.hprInterval(3, Point3(self.beefyManNP3.getH()+180,self.beefyManNP3.getP(),self.beefyManNP3.getR()),
                                                            startHpr=Point3(0, 0, 0))
        enemy3HprInterval2 = self.beefyManNP3.hprInterval(3, Point3(0, 0, 0),
                                                            startHpr=Point3(self.beefyManNP3.getH()+180, self.beefyManNP3.getP(),self.beefyManNP3.getR()))
        self.enemy3Pace = Sequence(enemy3PosInterval2,enemy3HprInterval1,
                                      enemy3PosInterval1, enemy3HprInterval2)

        self.enemy3Pace.loop()
        self.beefyManNP3.loop('walk')

        # #### Setting name
        # self.beefyManNP.setTag("Key", "Value")
        # value = self.beefyManNP.getTag("Key")
        # self.beefyManNP.setPythonTag("key", object)
        # object = self.beefyManNP.getPythonTag("key")
        # self.beefyManNP.setName("name-%i")

        # for  i in range(10):
        #     self.beefyManNP = Actor('models/beefy/beefy.egg',{
        #                             'walk':'models/beefy/beefy-walk.egg',
        #                             'idle':'models/beefy/beefy-idle.egg'})
        #     self.beefyManNP.reparentTo(render)
        #     self.beefyManNP.setScale(0.2)
        #     self.beefyManNP.setH(180)
        #     self.beefyManNP.setPos(i+3,i,3)
        #     #### Setting name
        #     #self.beefyManNP.setTag("Key", "Value")
        #     #value = self.beefyManNP.getTag("Key")
        #     #self.beefyManNP.setPythonTag("key", object)
        #     #object = self.beefyManNP.getPythonTag("key")
        #     self.beefyManNP.setName("name-%i")
        #     ####
            #self.bombNP.setPos(self.charracterNP.getPos())

#########################################################     ENEMY 5                           ########################################################################
        self.beefyManNP5 = Actor('models/beefy/beefy.egg',{
                                'walk':'models/beefy/beefy-walk.egg',
                                'idle':'models/beefy/beefy-idle.egg'})
        self.beefyManNP5.reparentTo(render)
        self.beefyManNP5.setScale(0.2)
#        self.beefyManNP1.setH(180)
        self.beefyManNP5.setPos(-60, 0, 11)
        enemy5PosInterval1 = self.beefyManNP5.posInterval(13, Point3(self.beefyManNP5.getX(),self.beefyManNP5.getY()+4,self.beefyManNP5.getZ()),
                                                      startPos=Point3(self.beefyManNP5.getX(),self.beefyManNP5.getY()-4,self.beefyManNP5.getZ()))
        enemy5PosInterval2 = self.beefyManNP5.posInterval(13, Point3(self.beefyManNP5.getX(),self.beefyManNP5.getY()-4,self.beefyManNP5.getZ()),
                                                      startPos=Point3(self.beefyManNP5.getX(),self.beefyManNP5.getY()+4,self.beefyManNP5.getZ()))
        enemy5HprInterval1 = self.beefyManNP5.hprInterval(3, Point3(self.beefyManNP5.getH()+180,self.beefyManNP5.getP(),self.beefyManNP5.getR()),
                                                      startHpr=Point3(0, 0, 0))
        enemy5HprInterval2 = self.beefyManNP5.hprInterval(3, Point3(0, 0, 0),
                                                      startHpr=Point3(self.beefyManNP5.getH()+180, self.beefyManNP5.getP(),self.beefyManNP5.getR()))
        self.enemy5Pace = Sequence(enemy5PosInterval2,enemy5HprInterval1,
                                enemy5PosInterval1, enemy5HprInterval2)

        self.enemy5Pace.loop()

        self.beefyManNP5.loop('walk')

#####################################################           ENEMY 6                    #############################################################################

        self.beefyManNP6 = Actor('models/beefy/beefy.egg',{
                                'walk':'models/beefy/beefy-walk.egg',
                                'idle':'models/beefy/beefy-idle.egg'})
        self.beefyManNP6.reparentTo(render)
        self.beefyManNP6.setScale(0.2)
#        self.beefyManNP1.setH(180)
        self.beefyManNP6.setPos(-63, 21, 11)
        enemy6PosInterval1 = self.beefyManNP6.posInterval(13, Point3(self.beefyManNP6.getX(),self.beefyManNP6.getY()+4,self.beefyManNP6.getZ()),
                                                      startPos=Point3(self.beefyManNP6.getX(),self.beefyManNP6.getY()-4,self.beefyManNP6.getZ()))
        enemy6PosInterval2 = self.beefyManNP6.posInterval(13, Point3(self.beefyManNP6.getX(),self.beefyManNP6.getY()-4,self.beefyManNP6.getZ()),
                                                      startPos=Point3(self.beefyManNP6.getX(),self.beefyManNP6.getY()+4,self.beefyManNP6.getZ()))
        enemy6HprInterval1 = self.beefyManNP6.hprInterval(3, Point3(self.beefyManNP6.getH()+180,self.beefyManNP6.getP(),self.beefyManNP6.getR()),
                                                      startHpr=Point3(0, 0, 0))
        enemy6HprInterval2 = self.beefyManNP6.hprInterval(3, Point3(0, 0, 0),
                                                      startHpr=Point3(self.beefyManNP6.getH()+180, self.beefyManNP6.getP(),self.beefyManNP6.getR()))
        self.enemy6Pace = Sequence(enemy6PosInterval2,enemy6HprInterval1,
                                enemy6PosInterval1, enemy6HprInterval2)

        self.enemy6Pace.loop()

        self.beefyManNP6.loop('walk')

#######################################################             ENEMY   7      ################################################################################

        self.beefyManNP7 = Actor('models/beefy/beefy.egg',{
                                'walk':'models/beefy/beefy-walk.egg',
                                'idle':'models/beefy/beefy-idle.egg'})
        self.beefyManNP7.reparentTo(render)
        self.beefyManNP7.setScale(0.2)
#        self.beefyManNP1.setH(180)
        self.beefyManNP7.setColor(1,0,1,1)
        #self.panda1.setColor(1,0,1,1)
        self.beefyManNP7.setPos(-67, 24, 11)
        self.beefyManNP7.loop('idle')

############################################################            MASTER          ############################################################################
        self.masterNP = Actor('models/lego/Cinder/Cinder.egg',{
                                'idle':'models/lego/Cinder/Cinder-jump.egg'})
        self.masterNP.reparentTo(render)
        self.masterNP.setScale(0.5)

#        self.beefyManNP1.setH(180)
        self.masterNP.setPos(-67, 21, 11.25)
        self.masterNP.loop('idle')

############################################################         ENEMY LEADER - THE EVIL SCIENTIST         #######################################################

        self.evilNP = Actor('models/lego/Scientist/Scientist.egg',{
                                'idle':'models/lego/Scientist/Scientist-taser.egg'})
        self.evilNP.reparentTo(render)
        self.evilNP.setScale(0.5)
#
        self.evilNP.setH(180)
        self.evilNP.setPos(-67, 19, 11.25)
        self.evilNP.loop('idle')
################################################################################################################################################################


    def setExpires(self, obj, val):
        obj.setPythonTag("expires", val)
        # Creates a bullet and adds it to the bullet list

    def setExpires(self, obj, val):
        obj.setPythonTag("expires", val)

    def secondaryFire(self):
        self.isFire = True
        obj = loader.loadModel("models/ball")
        obj.reparentTo(self.characterNP)
        # obj.setPos(self.characterNP.getPos())
        # obj.setHpr(self.characterNP.getHpr())

        obj.setScale(0.3)
        #obj.wrtReparentTo(render)
        # obj.setPos(self.characterNP.getX(),self.characterNP.getY(),self.characterNP.getZ())
        # obj.lookAt(self.characterNP.getPos())
        # obj.setH(self.characterNP.getH())
        #obj.setH(180)
        bulletInterval1 = obj.posInterval(0.3, Point3(obj.getX(), obj.getY() + 4, obj.getZ()),
                                                      startPos=Point3( obj.getX(), obj.getY(), obj.getZ()))
        bulletInterval1.start()



    def fire(self):

        #a =  int(round(time))
        self.isFire = True
        obj = loader.loadModel("models/ball")
        obj.reparentTo(render)
        obj.setScale(0.3)
        obj.setPos(self.characterNP.getX(),self.characterNP.getY()+0.3,self.characterNP.getZ()-2)
        obj.lookAt(self.characterNP.getPos())
        #print type(globalClock.getRealTime()), globalClock.getRealTime()
        obj.setTag("timer", str(globalClock.getRealTime()))
        self.bombs.append(obj)

    def enemyFire(self, object):

        #a =  int(round(time))
        self.isEnemyFire = True
        self.enemyObj = loader.loadModel("models/ball")
        self.enemyObj.reparentTo(render)
        self.enemyObj.setScale(0.3)
        self.enemyObj.setPos(object.getX(), object.getY(),object.getZ()-1.7)
        self.enemyObj.setTag("timerForEnemy", str(globalClock.getRealTime()))
        self.enemy1Bullet.append(self.enemyObj)

        # obj.setPos(self.characterNP.getX(),self.characterNP.getY()+0.3,self.characterNP.getZ()-2)
        # obj.lookAt(self.characterNP.getPos())

    def startGame(self):
        taskMgr.add('updateWorld')

game = CharacterController()
game.run()
