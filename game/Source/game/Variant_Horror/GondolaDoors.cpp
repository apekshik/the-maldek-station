#include "Variant_Horror/GondolaSystem.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"
#include "Components/AudioComponent.h"
#include "Components/SplineComponent.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "Sound/SoundAttenuation.h"
#include "TimerManager.h"

void AGondolaSystem::CreateDoorComponents()
{
 auto Mesh = [this](FName Name, USceneComponent* Parent)
 {
  auto* C = CreateDefaultSubobject<UStaticMeshComponent>(Name);
  C->SetupAttachment(Parent); C->SetMobility(EComponentMobility::Movable);
  C->SetCollisionEnabled(ECollisionEnabled::NoCollision); return C;
 };
 // FBX basis is (x,-y,z); the established cabin placement adds a 180-degree yaw.
 DoorLeft = Mesh(TEXT("DoorLeft"), GondolaMesh);
 DoorRight = Mesh(TEXT("DoorRight"), GondolaMesh);
 DoorLeft->SetRelativeRotation(FRotator(0,180,0));
 DoorRight->SetRelativeRotation(FRotator(0,180,0));
 DoorPinion = Mesh(TEXT("DoorPinion"), GondolaMesh);
 DoorPinion->SetRelativeLocation(FVector(0,-312.5,218.5));
 for (int32 I=0; I<8; ++I)
 {
  auto* C = Mesh(*FString::Printf(TEXT("DoorRoller%d"),I), I<4 ? DoorLeft.Get() : DoorRight.Get());
  const float Sign = I<4 ? -1.f : 1.f;
  C->SetRelativeLocation(FVector(Sign*30.7f + ((I%4)/2==0 ? -15.f : 15.f),317.7f,I%2==0 ? 214.5f : 222.5f));
  DoorRollers.Add(C);
 }
 auto Collision = [this](FName Name, UStaticMeshComponent* Parent, float X)
 {
  auto* C=CreateDefaultSubobject<UBoxComponent>(Name); C->SetupAttachment(Parent);
  C->SetRelativeLocation(FVector(X,316,104)); C->SetBoxExtent(FVector(30.3f,3.5f,104));
  C->SetCollisionProfileName(TEXT("BlockAll")); C->SetGenerateOverlapEvents(false); return C;
 };
 DoorLeftCollision=Collision(TEXT("DoorLeftCollision"),DoorLeft,-30.3f);
 DoorRightCollision=Collision(TEXT("DoorRightCollision"),DoorRight,30.3f);
 DoorAudio=CreateDefaultSubobject<UAudioComponent>(TEXT("DoorAudio"));
 DoorAudio->SetupAttachment(GondolaMesh); DoorAudio->SetRelativeLocation(FVector(0,-308,212));
 DoorAudio->bAutoActivate=false; DoorAudio->bOverrideAttenuation=true;
 DoorAudio->AttenuationOverrides.bAttenuate=true;
 DoorAudio->AttenuationOverrides.bSpatialize=true;
 DoorAudio->AttenuationOverrides.AttenuationShape=EAttenuationShape::Sphere;
 DoorAudio->AttenuationOverrides.AttenuationShapeExtents=FVector(220);
 DoorAudio->AttenuationOverrides.FalloffDistance=1800;
 DoorAudio->SetVolumeMultiplier(1.5f);
}
bool AGondolaSystem::HasSlidingDoors() const
{ return DoorLeft && DoorRight && DoorLeft->GetStaticMesh() && DoorRight->GetStaticMesh(); }

bool AGondolaSystem::BridgeOccupied() const
{
 if (!IsValid(FarBoardingBridge)) return false;
 for (TActorIterator<APawn> It(GetWorld()); It; ++It)
 {
  float R,H; It->GetSimpleCollisionCylinder(R,H);
  const FVector P=It->GetActorLocation()-FarBoardingBridge->GetActorLocation();
  if (FMath::Abs(P.X)<160+R && FMath::Abs(P.Y)<100+R && P.Z+H>0 && P.Z-H<200) return true;
 }
 return false;
}
bool AGondolaSystem::DoorwayOccupied() const
{
 for (TActorIterator<APawn> It(GetWorld()); It; ++It)
 {
  float R,H; It->GetSimpleCollisionCylinder(R,H);
  const FVector P=GondolaMesh->GetComponentTransform().InverseTransformPosition(It->GetActorLocation());
  // Include the approaching capsule, both leaves' swept space and both sides of the sill.
  if (FMath::Abs(P.X)<124+R && FMath::Abs(P.Y+316)<35+R && P.Z+H>0 && P.Z-H<211) return true;
 }
 return false;
}
bool AGondolaSystem::LandingReady() const
{ return !bWaitingAtMaldek || !IsValid(FarBoardingBridge) || FarBoardingBridge->GetActorLocation().Equals(FarBridgeDeployed,1.f); }

void AGondolaSystem::ApplyDoorPose()
{
 const bool Enabled=HasSlidingDoors();
 DoorLeftCollision->SetCollisionEnabled(Enabled ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
 DoorRightCollision->SetCollisionEnabled(Enabled ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
 DoorOpenFraction=DoorTravel*DoorTravel*(3.f-2.f*DoorTravel);
 DoorLeft->SetRelativeLocation(FVector(63.5f*DoorOpenFraction,0,0));
 DoorRight->SetRelativeLocation(FVector(-63.5f*DoorOpenFraction,0,0));
 DoorPinion->SetRelativeRotation(FRotator(-FMath::RadiansToDegrees(.635f*DoorOpenFraction/.034f),180,0));
 for (int32 I=0;I<DoorRollers.Num();++I)
  DoorRollers[I]->SetRelativeRotation(FRotator(FMath::RadiansToDegrees((I<4 ? -1.f : 1.f)*.635f*DoorOpenFraction/.026f),0,0));
}
void AGondolaSystem::PlayDoorRecording(USoundBase* Sound)
{
 DoorAudio->Stop();
 if (Sound) { DoorAudio->SetSound(Sound); DoorAudio->Play(); }
}
void AGondolaSystem::StartDoorOpening()
{
 DoorPhase=EGondolaDoorPhase::Opening; DoorPhaseTime=0;
 PlayDoorRecording(DoorOpenSound);
}
void AGondolaSystem::RequestDeparture(float TravelDirection)
{
 if (bMoving || bArrivalPending || bDepartureRequested) return;
 GetWorldTimerManager().ClearTimer(MaldekWaitTimer);
 bDepartureRequested=true; RequestedDirection=TravelDirection;
}
void AGondolaSystem::StartDeparture()
{
 if (DoorPhase!=EGondolaDoorPhase::Closed || DoorOpenFraction>0.f || DoorwayOccupied() || BridgeOccupied()) return;
 bDepartureRequested=false; bReturnRequested=false;
 bDocked=false; bWaitingAtMaldek=false; bMoving=true;
 Direction=RequestedDirection; CurrentSpeed=0.f;
 OnGondolaDeparted.Broadcast();
}
void AGondolaSystem::UpdateDoors(float Dt)
{
 if (!HasSlidingDoors() || Dt<=0) return;
 const bool Obstructed=DoorwayOccupied() || (bWaitingAtMaldek && BridgeOccupied());
 if ((DoorPhase==EGondolaDoorPhase::Closing || DoorPhase==EGondolaDoorPhase::Latching) && Obstructed)
  StartDoorOpening();
 switch (DoorPhase)
 {
 case EGondolaDoorPhase::Settling:
  if (!bMoving && LandingReady()) { DoorPhaseTime+=Dt; if (DoorPhaseTime>=.75f) StartDoorOpening(); }
  break;
 case EGondolaDoorPhase::Opening:
  DoorTravel=FMath::Min(1.f,DoorTravel+Dt/3.5f);
  if (DoorTravel>=1.f)
  {
   DoorPhase=EGondolaDoorPhase::Open; DoorPhaseTime=0;
   if (bWaitingAtMaldek && !bDepartureRequested)
   {
    if (WaitTimeAtMaldek>0) GetWorldTimerManager().SetTimer(MaldekWaitTimer,this,&AGondolaSystem::ReturnGondola,WaitTimeAtMaldek,false);
    else RequestDeparture(-1.f);
   }
  }
  break;
 case EGondolaDoorPhase::Open:
  DoorPhaseTime=Obstructed ? 0.f : DoorPhaseTime+Dt;
  if (bDepartureRequested && DoorPhaseTime>=1.f && !Obstructed)
  { DoorPhase=EGondolaDoorPhase::Closing; PlayDoorRecording(DoorCloseSound); }
  break;
 case EGondolaDoorPhase::Closing:
  DoorTravel=FMath::Max(0.f,DoorTravel-Dt/1.75f);
  if (DoorTravel<=0) { DoorPhase=EGondolaDoorPhase::Latching; DoorPhaseTime=0; }
  break;
 case EGondolaDoorPhase::Latching:
  DoorPhaseTime+=Dt;
  if (DoorPhaseTime>=.6f) { DoorPhase=EGondolaDoorPhase::Closed; bReturnRequested=RequestedDirection<0; }
  break;
 case EGondolaDoorPhase::Closed:
  if (bDepartureRequested && Obstructed)
  {
   // Restore the landing before reopening if someone enters after the latch hold.
   bReturnRequested=false; DoorPhase=EGondolaDoorPhase::Settling; DoorPhaseTime=0; break;
  }
  if (bDepartureRequested && (!bWaitingAtMaldek || !IsValid(FarBoardingBridge) || FarBoardingBridge->GetActorLocation().Equals(FarBridgeParked,1.f))) StartDeparture();
  break;
 }
 ApplyDoorPose();
}
