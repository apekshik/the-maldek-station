#include "StationCableAudio.h"
#include "Components/AudioComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Sound/SoundAttenuation.h"

AStationCableAudio::AStationCableAudio()
{
 PrimaryActorTick.bCanEverTick=true;
 Audio=CreateDefaultSubobject<UAudioComponent>(TEXT("CableAudio"));
 SetRootComponent(Audio);Audio->bAutoActivate=false;
 Audio->bOverrideAttenuation=true;
 auto& S=Audio->AttenuationOverrides;
 S.bAttenuate=true;S.bSpatialize=true;
 S.DistanceAlgorithm=EAttenuationDistanceModel::Linear;
 S.AttenuationShapeExtents=FVector(250,0,0);S.FalloffDistance=6500;
 S.bAttenuateWithLPF=true;S.LPFRadiusMin=500;S.LPFRadiusMax=6500;
 S.LPFFrequencyAtMin=18000;S.LPFFrequencyAtMax=1800;
 S.bEnableOcclusion=true;S.OcclusionVolumeAttenuation=.45f;
 S.OcclusionLowPassFilterFrequency=2000;S.OcclusionInterpolationTime=.4f;
}
void AStationCableAudio::BeginPlay()
{
 Super::BeginPlay();Audio->SetSound(CableLoop);
}
void AStationCableAudio::Tick(float Dt)
{
 Super::Tick(Dt);
 if(!IsValid(GondolaTarget) || !CableLoop){Audio->Stop();MotionAmount=0;bHasLocation=false;return;}
 // Use the moving cabin mesh, not the actor bounds (which include the entire cable spline).
 const UStaticMeshComponent* Mesh=GondolaTarget->FindComponentByClass<UStaticMeshComponent>();
 FVector Center=Mesh?Mesh->Bounds.Origin:GondolaTarget->GetActorLocation();
 FVector Extent=Mesh?Mesh->Bounds.BoxExtent:FVector::ZeroVector;
 const float Distance=bHasLocation?FVector::Distance(Center,PreviousLocation):0;
 const float Speed=Dt>SMALL_NUMBER?Distance/Dt:0;
 PreviousLocation=Center;bHasLocation=true;
 SetActorLocation(Center+FVector(0,0,Extent.Z+30));
 // Ignore scene teleports; playback represents continuous physical travel.
 const float Target=Speed>2 && Speed<3000?FMath::Clamp(Speed/100.f,.2f,1.f):0;
 MotionAmount=FMath::FInterpTo(MotionAmount,Target,Dt,Target>MotionAmount?2.f:3.f);
 Audio->SetVolumeMultiplier(CableVolume*MotionAmount);
 if(MotionAmount>.01f){if(!Audio->IsPlaying())Audio->Play();}
 else if(Audio->IsPlaying())Audio->Stop();
}
