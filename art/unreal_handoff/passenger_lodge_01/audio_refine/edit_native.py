from pathlib import Path
p=Path('game/Source/game/Variant_Horror')
(p/'StationSoundVariation.h').write_text('''#pragma once
#include "CoreMinimal.h"
#include "Sound/SoundBase.h"
// Select a recorded take without repeating the previous take on this actor.
inline USoundBase* PickStationSound(USoundBase* Fallback,const TArray<TObjectPtr<USoundBase>>& Takes,TWeakObjectPtr<USoundBase>& Previous)
{
 TArray<USoundBase*,TInlineAllocator<8>> Valid;
 for(auto S:Takes)if(S)Valid.AddUnique(S.Get());
 if(Valid.Num()>1)Valid.Remove(Previous.Get());
 USoundBase* Result=Valid.IsEmpty()?Fallback:Valid[FMath::RandHelper(Valid.Num())];
 Previous=Result;return Result;
}
''')
f=p/'StationDoor.h';s=f.read_text().replace(' TObjectPtr<UCameraComponent> KeypadCamera;',' TObjectPtr<UCameraComponent> KeypadCamera;\n UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Door|Key") FVector KeyCameraOffset=FVector(18,35,14);');s=s.replace(' void PlayDoorSound(',''' UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Door|Audio") TArray<TObjectPtr<USoundBase>> OpeningTakes;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Door|Audio") TArray<TObjectPtr<USoundBase>> ClosingTakes;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Door|Audio") TArray<TObjectPtr<USoundBase>> CloseImpactTakes;
 UPROPERTY(Transient) TObjectPtr<USoundBase> ActiveTravelSound;
 TWeakObjectPtr<USoundBase> LastOpeningTake,LastClosingTake,LastImpactTake;
 void PlayDoorSound(''');f.write_text(s)
f=p/'StationDoor.cpp';s=f.read_text().replace('#include "Camera/CameraComponent.h"','#include "Camera/CameraComponent.h"\n#include "StationSoundVariation.h"');s=s.replace('T.TransformPosition(FVector(18,35,14))','T.TransformPosition(KeyCameraOffset)');s=s.replace('TargetAngle=FMath::IsNearlyZero(TargetAngle)?OpenAngle:0.f;bObstructed=false;','''TargetAngle=FMath::IsNearlyZero(TargetAngle)?OpenAngle:0.f;bObstructed=false;
 ActiveTravelSound=FMath::IsNearlyZero(TargetAngle)?PickStationSound(ClosingMovementSound?ClosingMovementSound.Get():MovementSound.Get(),ClosingTakes,LastClosingTake):PickStationSound(MovementSound,OpeningTakes,LastOpeningTake);''');s=s.replace('USoundBase* TravelSound=bClosing && ClosingMovementSound?ClosingMovementSound.Get():MovementSound.Get();','USoundBase* TravelSound=ActiveTravelSound?ActiveTravelSound.Get():(bClosing && ClosingMovementSound?ClosingMovementSound.Get():MovementSound.Get());');s=s.replace('MotionAudio->Stop();PlayDoorSound(CloseSound);','MotionAudio->Stop();PlayDoorSound(PickStationSound(CloseSound,CloseImpactTakes,LastImpactTake));');f.write_text(s)
f=p/'StationCabinet.h';s=f.read_text().replace('private:', ''' UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<TObjectPtr<USoundBase>> OpeningTakes;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<TObjectPtr<USoundBase>> ClosingTakes;
private:
 TWeakObjectPtr<USoundBase> LastOpeningTake,LastClosingTake;''');f.write_text(s)
f=p/'StationCabinet.cpp';s=f.read_text().replace('#include "StationCabinet.h"','#include "StationCabinet.h"\n#include "StationSoundVariation.h"');s=s.replace('bWantsOpen?MovementSound.Get():ClosingSound.Get()','bWantsOpen?PickStationSound(MovementSound,OpeningTakes,LastOpeningTake):PickStationSound(ClosingSound,ClosingTakes,LastClosingTake)');f.write_text(s)
f=p/'SurfaceFootstepComponent.h';s=f.read_text().replace('\tTArray<TObjectPtr<USoundBase>> WoodSteps;','\tTArray<TObjectPtr<USoundBase>> WoodSteps;\n\tUPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Footsteps")\n\tTArray<TObjectPtr<USoundBase>> TileSteps;');f.write_text(s)
f=p/'SurfaceFootstepComponent.cpp';s=f.read_text().replace('case 5: Samples = &WoodSteps; break;','case 5: Samples = &WoodSteps; break;\n\tcase 6: Samples = &TileSteps; break;');f.write_text(s)
f=Path('game/Config/DefaultEngine.ini');s=f.read_text();s=s.replace('+PhysicalSurfaces=(Type=SurfaceType5,Name="Wood")','+PhysicalSurfaces=(Type=SurfaceType5,Name="Wood")\n+PhysicalSurfaces=(Type=SurfaceType6,Name="Tile")');f.write_text(s)
(p/'StationLodgeAcoustics.h').write_text('''#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StationLodgeAcoustics.generated.h"
class UAudioComponent;
class USoundBase;
UCLASS(Blueprintable)
class GAME_API AStationLodgeAcoustics: public AActor
{
 GENERATED_BODY()
public:
 AStationLodgeAcoustics();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<UAudioComponent> WindAudio;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TObjectPtr<USoundBase> WindLoop;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<FVector> RoomCenters;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<FVector> RoomExtents;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float Volume=.8f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,meta=(ClampMin="0",ClampMax="1")) float StormIntensity=1;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Transient) float InteriorBlend=0;
 UFUNCTION(BlueprintPure) float WeightAt(FVector WorldPosition) const;
};
''')
(p/'StationLodgeAcoustics.cpp').write_text('''#include "StationLodgeAcoustics.h"
#include "Components/AudioComponent.h"
#include "Components/SceneComponent.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/PlayerController.h"
#include "Sound/SoundBase.h"
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
 InteriorBlend=FMath::FInterpConstantTo(InteriorBlend,Target,Dt,.8f);
 WindAudio->SetVolumeMultiplier(InteriorBlend*Volume);
}
''')
print('Native camera, sound variants, tile routing and sheltered wind changes written')
