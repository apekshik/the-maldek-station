#include "StationLodgeAcoustics.h"
#include "Components/AudioComponent.h"
#include "Components/SceneComponent.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/PlayerController.h"
#include "Sound/SoundBase.h"
#include "UObject/UnrealType.h"
AStationLodgeAcoustics::AStationLodgeAcoustics()
{
 PrimaryActorTick.bCanEverTick=true;
 RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
 WindAudio=CreateDefaultSubobject<UAudioComponent>(TEXT("ShelteredWind"));WindAudio->SetupAttachment(RootComponent);
 WindAudio->bAutoActivate=false;WindAudio->bAllowSpatialization=false;
}
void AStationLodgeAcoustics::BeginPlay()
{
 Super::BeginPlay();WindAudio->SetSound(WindLoop);WindAudio->SetVolumeMultiplier(0);WindAudio->Play();
}
float AStationLodgeAcoustics::WeightAt(FVector WorldPosition) const
{
 const FVector P=GetActorTransform().InverseTransformPosition(WorldPosition);float Weight=0;
 for(int32 I=0;I<FMath::Min(RoomCenters.Num(),RoomExtents.Num());++I)
 {
  const FVector D=(P-RoomCenters[I]).GetAbs()-RoomExtents[I];
  if(D.Z>0)continue;
  // A narrow, continuous threshold blend; separate annex boxes exclude the open court.
  Weight=FMath::Max(Weight,FMath::Clamp(.5f-FMath::Max(D.X,D.Y)/60.f,0.f,1.f));
 }
 return Weight;
}
void AStationLodgeAcoustics::Tick(float Dt)
{
 Super::Tick(Dt);auto PC=UGameplayStatics::GetPlayerController(this,0);
 FVector P;FRotator R;float Target=0;
 if(PC && PC->GetPawn()){PC->GetPlayerViewPoint(P,R);Target=WeightAt(P)*FMath::Clamp(StormIntensity,0.f,1.f);}
 if(WeatherActor)
 {
  if(auto Property=FindFProperty<FNumericProperty>(WeatherActor->GetClass(),TEXT("Wind Intensity")))
  {
   const void* Value=Property->ContainerPtrToValuePtr<void>(WeatherActor);
   const double Wind=Property->IsFloatingPoint()?Property->GetFloatingPointPropertyValue(Value):double(Property->GetSignedIntPropertyValue(Value));
   Target*=FMath::Clamp(float(Wind/2.),0.f,1.f);
  }
 }
 InteriorBlend=FMath::FInterpConstantTo(InteriorBlend,Target,Dt,.8f);
 WindAudio->SetVolumeMultiplier(InteriorBlend*Volume);
}
