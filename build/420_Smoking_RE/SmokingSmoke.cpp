// SPDX-License-Identifier: GPL-3.0-or-later
// Optional RE_Kenshi extension; no persistent character or save-data state.
#include <kenshi/GameWorld.h>
#include <kenshi/Character.h>
#include <kenshi/Animation/AnimationClass.h>
#include <kenshi/Renderer.h>
#include <core/Functions.h>
#include <Debug.h>
#include <ogre/OgreSceneManager.h>
#include <ogre/OgreSceneNode.h>
#include <ogre/OgreBillboardSet.h>
#include <ogre/OgreBillboard.h>
#include <ogre/OgreMaterialManager.h>
#include <ogre/OgreMaterial.h>
#include <ogre/OgreTechnique.h>
#include <ogre/OgrePass.h>
#include <ogre/OgreAnimationState.h>
#include <ogre/OgreException.h>
#include <ogre/OgreGpuProgramParams.h>
#include <ogre/OgreOldBone.h>
#include <vector>
#include <map>
#include <cmath>
#include <algorithm>
#include <sstream>

namespace {
const char* kMaterial = "420/ExhaledSmoke";
const unsigned kMaxPuffs = 2304;
const float kExhaleAmountMultiplier = 3.0f;
const float kExhaleSpreadMultiplier = 3.0f;
// Tip smoke must remain visible against interiors without becoming an exhale cloud.
const float kTipRate = 9.0f;
const float kTipSize = .30f;
const float kTipOpacity = .28f;
struct Puff {
    Ogre::Vector3 position, velocity;
    float age, life, size, opacity;
};
struct Emitter {
    float mouthCredit, tipCredit;
    Emitter() : mouthCredit(0), tipCredit(0) {}
};
std::vector<Puff> puffs;
std::map<Character*, Emitter> emitters;
Ogre::SceneManager* scene = 0;
Ogre::BillboardSet* boards = 0;
Ogre::SceneNode* smokeNode = 0;
Ogre::Vector3 previousOrigin = Ogre::Vector3::ZERO;
bool disabled = false;
unsigned randomState = 420;
float diagnosticClock = 0;
unsigned diagnosticCount = 0;
float random01() { randomState = 1664525 * randomState + 1013904223; return (randomState >> 8) / 16777216.0f; }

Ogre::Vector3 bonePoint(AnimationClassBase* animation, const char* name, const Ogre::Vector3& offset) {
    Ogre::OldBone* bone = animation->_getBone(name);
    return animation->node->_getFullTransform().transformAffine(
        bone->_getDerivedPosition() + bone->_getDerivedOrientation() * offset);
}

void releaseSmoke() {
    emitters.clear(); puffs.clear();
    if (scene && boards) scene->destroyBillboardSet(boards);
    if (scene && smokeNode) scene->destroySceneNode(smokeNode);
    boards = 0; smokeNode = 0; scene = 0;
}

bool ensureSmoke(Renderer* render) {
    Ogre::SceneManager* current = render->getSceneManager();
    if (!current) return false;
    if (scene != current) {
        // A replaced scene owns and has already released its old movable objects.
        boards = 0; smokeNode = 0; puffs.clear(); emitters.clear();
        scene = current; previousOrigin = render->getSceneRelativeOrigin();
    }
    if (boards) return true;
    Ogre::MaterialPtr material = Ogre::MaterialManager::getSingleton().getByName(kMaterial);
    if (material.isNull()) {
        Ogre::MaterialPtr base = Ogre::MaterialManager::getSingleton().getByName("kenshi_smoke1");
        if (base.isNull()) return false; // Game resources may not have loaded yet.
        material = base->clone(kMaterial);
        Ogre::Pass* pass = material->getTechnique(0)->getPass(0);
        pass->setVertexProgram("Basic_Coloured_Texture_VP");
        pass->setSceneBlending(Ogre::SBT_TRANSPARENT_ALPHA);
        pass->setDepthCheckEnabled(true);
        pass->setDepthWriteEnabled(false);
        pass->getFragmentProgramParameters()->setNamedConstant("colour", Ogre::Vector4(1,1,1,1));
    }
    boards = scene->createBillboardSet(kMaxPuffs);
    // main.compositor draws forward particles in queues 82..84, after lighting.
    boards->setRenderQueueGroup(83);
    boards->setMaterialName(kMaterial);
    boards->setAutoextend(false);
    boards->setVisibilityFlags(0xFFFFFFFF);
    boards->setVisible(true);
    boards->setBillboardsInWorldSpace(true);
    smokeNode = scene->getRootSceneNode()->createChildSceneNode();
    smokeNode->attachObject(boards);
    DebugLog("420 Smoke: billboard renderer ready");
    return true;
}

void spawn(const Ogre::Vector3& position, const Ogre::Vector3& forward, bool mouth) {
    if (puffs.size() >= kMaxPuffs) return;
    Puff p;
    p.position = position;
    p.velocity = mouth ? forward * 2.0f : Ogre::Vector3::ZERO;
    const float spread = mouth ? kExhaleSpreadMultiplier : 1.0f;
    p.velocity += Ogre::Vector3((random01()-.5f)*.18f*spread, mouth ? .35f : .55f, (random01()-.5f)*.18f*spread);
    p.age = 0; p.life = mouth ? 1.8f : 2.5f;
    p.size = mouth ? .52f*kExhaleSpreadMultiplier : kTipSize; p.opacity = mouth ? .18f : kTipOpacity;
    puffs.push_back(p);
}

void updateSmoke(GameWorld* world, float elapsed) {
    if (!world->initialized || !world->render) return;
    Renderer* render = dynamic_cast<Renderer*>(world->render);
    if (!render || !ensureSmoke(render)) return;
    const float dt = world->paused ? 0.0f : std::max(0.0f, std::min(elapsed, .25f));
    diagnosticClock += dt;
    Ogre::Vector3 origin = render->getSceneRelativeOrigin();
    Ogre::Vector3 shift = previousOrigin - origin;
    previousOrigin = origin;
    for (size_t i=0; i<puffs.size();) {
        Puff& p = puffs[i]; p.age += dt;
        if (p.age >= p.life) { puffs[i] = puffs.back(); puffs.pop_back(); continue; }
        p.position += shift + p.velocity * dt;
        ++i;
    }
    std::map<Character*, Emitter> active;
    const ogre_unordered_set<Character*>::type& characters = world->getCharacterUpdateList();
    for (ogre_unordered_set<Character*>::type::const_iterator it=characters.begin(); it!=characters.end(); ++it) {
        Character* character = *it;
        if (!character || world->getIsInKillList(character)) continue;
        AnimationClassBase* animation = character->getAnimationClass();
        if (!animation || !animation->getVisible()) continue;
        const char* names[] = { "420_smoke_chillum", "420_smoke_joint", "420_recline_chillum", "420_recline_joint" };
        int kind = -1;
        AnimationClassBase::SingleAnimation* playing = 0;
        for (int i=0; i<4; ++i) {
            playing = animation->getAnimationPlaying_animName(names[i]);
            if (playing && playing->mainState && diagnosticClock >= 2 && diagnosticCount < 12) {
                std::ostringstream message;
                message << "420 Smoke sample: " << names[i] << " t=" << playing->mainState->getTimePosition()
                    << " enabled=" << playing->mainState->getEnabled() << " weight=" << playing->weight
                    << " wanted=" << playing->stillWanted << " stop=" << playing->msgHardStop
                    << " speed=" << playing->speed << " masterSpeed=" << animation->masterSpeed
                    << " head=" << animation->getBoneWorldPosition("Bip01 Head", 1.0f)
                    << " origin=" << origin << " puffs=" << puffs.size();
                message << " node=" << animation->node->_getDerivedPosition()
                    << " scale=" << animation->node->_getDerivedScale()
                    << " directHead=" << bonePoint(animation,"Bip01 Head",Ogre::Vector3::ZERO);
                message << " smokeNode=" << smokeNode->_getDerivedPosition()
                    << " visible=" << boards->isVisible() << " mask=" << boards->getVisibilityFlags();
                DebugLog(message.str()); diagnosticClock=0; ++diagnosticCount;
            }
            if (playing && playing->mainState && playing->mainState->getEnabled()
                && playing->weight > .05f && !playing->msgHardStop) { kind=i%2; break; }
        }
        if (kind < 0 || !animation->getHasBone("Bip01 Head")) continue;
        Emitter state = emitters[character];
        float t = playing->mainState->getTimePosition();
        bool exhaling = t >= 8.0f && t < 11.0f;
        if (exhaling) state.mouthCredit += dt * 24.0f*kExhaleAmountMultiplier;
        else state.mouthCredit = 0;
        Ogre::Quaternion headRotation = animation->getBoneWorldOrientation("Bip01 Head");
        // Lucius exporter converts Blender bone axes with fix * rot.
        // Inverse conversion maps the Blender mouth offset to (y,z,x).
        Ogre::Vector3 forward = headRotation * Ogre::Vector3(.006f,0,-1);
        Ogre::Vector3 mouth = bonePoint(animation,"Bip01 Head",Ogre::Vector3(.1818f,0,-1.5344f));
        while (state.mouthCredit >= 1) { spawn(mouth, forward, true); state.mouthCredit -= 1; }
        if (animation->getHasBone("Bip01 Prop2")) {
            state.tipCredit += dt * kTipRate;
            Ogre::Vector3 tip = bonePoint(animation,"Bip01 Prop2",Ogre::Vector3(0,kind==0 ? 1.79f : 1.23f,0));
            while (state.tipCredit >= 1) { spawn(tip, forward, false); state.tipCredit -= 1; }
        }
        active[character] = state;
    }
    emitters.swap(active); // No dereference of characters retained from previous frames.
    boards->clear();
    for (size_t i=0; i<puffs.size(); ++i) {
        const Puff& p = puffs[i]; float age = p.age/p.life;
        float alpha = p.opacity * std::sin(3.14159265f*age);
        Ogre::Billboard* b = boards->createBillboard(p.position, Ogre::ColourValue(.72f,.74f,.76f,alpha));
        float size = p.size*(.4f+2.0f*age);
        b->setDimensions(size,size);
    }
    boards->_updateBounds();
}

void (*originalAnimationUpdate)(AnimationClassBase::SingleAnimation*,float,float,bool) = 0;
void animationUpdateHook(AnimationClassBase::SingleAnimation* animation, float masterTime, float frameTime, bool sounds) {
    // Apply immediately before advancement; furniture resets speed each frame.
    if (animation->animName == "420_smoke_chillum" || animation->animName == "420_smoke_joint"
        || animation->animName == "420_recline_chillum" || animation->animName == "420_recline_joint")
        animation->speed = 1.0f;
    originalAnimationUpdate(animation, masterTime, frameTime, sounds);
}

void disableSmokeAfterError() {
    disabled = true;
    emitters.clear(); puffs.clear();
    if (!boards) return;
    // Hide first so a failed clear cannot leave frozen smoke on screen.
    // Keep ownership until normal world cleanup; the renderer is already failing.
    try { boards->setVisible(false); }
    catch (const Ogre::Exception&) {}
    try { boards->clear(); }
    catch (const Ogre::Exception&) {}
}

void (*originalUpdate)(GameWorld*,float) = 0;
void updateHook(GameWorld* world, float elapsed) {
    originalUpdate(world,elapsed);
    if (disabled) return;
    try { updateSmoke(world,elapsed); }
    catch (const Ogre::Exception& e) {
        disableSmokeAfterError();
        ErrorLog(std::string("420 Smoke disabled after renderer error: ")+e.getFullDescription());
    }
}
void (*originalClear)(GameWorld*) = 0;
void clearHook(GameWorld* world) {
    releaseSmoke(); disabled=false;
    originalClear(world);
}
}

__declspec(dllexport) void startPlugin() {
    if (KenshiLib::AddHook(KenshiLib::GetRealAddress(&AnimationClassBase::SingleAnimation::update),
        &animationUpdateHook,&originalAnimationUpdate) != KenshiLib::SUCCESS) {
        ErrorLog("420 Smoke: animation timing hook failed; plugin inactive"); return;
    }
    // Cleanup must be installed first; never emit without a working cleanup hook.
    if (KenshiLib::AddHook(KenshiLib::GetRealAddress(&GameWorld::_clearAndDestroyGameWorldStuff),
        &clearHook,&originalClear) != KenshiLib::SUCCESS) {
        ErrorLog("420 Smoke: cleanup hook failed; plugin inactive"); return;
    }
    if (KenshiLib::AddHook(KenshiLib::GetRealAddress(&GameWorld::_NV_mainLoop_GPUSensitiveStuff),
        &updateHook,&originalUpdate) != KenshiLib::SUCCESS) {
        ErrorLog("420 Smoke: update hook failed; plugin inactive"); return;
    }
    DebugLog("420 Smoke: hooks installed; exhale window [8,11) seconds");
}
