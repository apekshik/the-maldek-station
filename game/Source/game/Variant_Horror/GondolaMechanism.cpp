#include "GondolaMechanism.h"
#include "GondolaSystem.h"
#include "Components/StaticMeshComponent.h"
#include "Components/AudioComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/GameplayStatics.h"

AGondolaMechanism::AGondolaMechanism()
{
 PrimaryActorTick.bCanEverTick=true;
 PrimaryActorTick.TickGroup=TG_PostPhysics;
 SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("MechanismRoot")));
}
void AGondolaMechanism::BeginPlay()
{
 Super::BeginPlay();
 if(Gondola) { AddTickPrerequisiteActor(Gondola); InitialDistance=PreviousDistance=Gondola->GetRouteDistance(); }
 for(const auto& R:Rotors)
 {
  RestRotations.Add(IsValid(R.Actor)?R.Actor->GetActorQuat():FQuat::Identity);
  if(IsValid(R.Actor)&&R.Actor->GetRootComponent())R.Actor->GetRootComponent()->SetMobility(EComponentMobility::Movable);
 }
 for(AActor* A:RopeParts)if(IsValid(A))
  if(auto* M=A->FindComponentByClass<UStaticMeshComponent>())
   if(auto* D=M->CreateDynamicMaterialInstance(0))RopeMaterials.Add(D);
 for(const auto& S:SoundSources)if(IsValid(S.Actor))
  if(auto* A=S.Actor->FindComponentByClass<UAudioComponent>()) { A->Stop(); A->SetVolumeMultiplier(0); }
}
void AGondolaMechanism::Tick(float Dt)
{
 Super::Tick(Dt);
 if(!IsValid(Gondola)||Dt<=SMALL_NUMBER)return;
 const float Distance=Gondola->GetRouteDistance();
 // Capture after all BeginPlay staging, regardless of level actor initialization order.
 if(!bHasInitialTick) { InitialDistance=PreviousDistance=Distance; bHasInitialTick=true; }
 SignedSpeedCm=(Distance-PreviousDistance)/Dt; PreviousDistance=Distance;
 RopeTravelMeters=(double(Distance)-InitialDistance)/100.;
 for(int32 I=0;I<Rotors.Num()&&I<RestRotations.Num();++I)
 {
  const auto& R=Rotors[I];
  if(!IsValid(R.Actor)||R.PitchRadiusCm<=SMALL_NUMBER)continue;
  const double Angle=FMath::Fmod(RopeTravelMeters*100.*R.Ratio/R.PitchRadiusCm,2.*PI);
  R.Actor->SetActorRotation(FQuat(R.WorldAxis.GetSafeNormal(),Angle)*RestRotations[I],ETeleportType::None);
 }
 // UV.x is unwrapped loop distance in metres. One shared phase follows physical travel.
 for(UMaterialInstanceDynamic* M:RopeMaterials)if(M)M->SetScalarParameterValue(TEXT("RopeTravelMeters"),float(RopeTravelMeters));
 const bool Moving=Gondola->IsMoving();
 if(Moving!=bWasMoving)
 {
  USoundBase* Cue=Moving?BrakeReleaseSound:BrakeSetSound;
  if(Cue)UGameplayStatics::PlaySoundAtLocation(this,Cue,BrakeLocation,FRotator::ZeroRotator,.85f,1.f,0.f,BrakeAttenuation);
  bWasMoving=Moving;
 }
 const float SpeedFraction=FMath::Clamp(FMath::Abs(SignedSpeedCm)/FMath::Max(Gondola->CruiseSpeed,1.f),0.f,1.f);
 SoundMotion=FMath::FInterpTo(SoundMotion,Moving?FMath::Lerp(.38f,1.f,SpeedFraction):0.f,Dt,Moving?5.f:12.f);
 for(const auto& S:SoundSources)if(IsValid(S.Actor))
  if(auto* A=S.Actor->FindComponentByClass<UAudioComponent>())
  {
   const float Volume=FMath::Lerp(S.IdleVolume,S.RunningVolume,SoundMotion);
   A->SetVolumeMultiplier(Volume);
   A->SetPitchMultiplier(FMath::Lerp(S.MinimumPitch,S.MaximumPitch,SpeedFraction));
   if(Volume>.005f) { if(!A->IsPlaying())A->Play(); }
   else if(A->IsPlaying())A->Stop();
  }
}
